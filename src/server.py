import os
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import uvicorn
import argparse
from designgalleries import generate
from designspace import DesignSpace, Generation, Tag, Example
from domains.ui.ui import UIGen
from domains.domain import Domain
from domains.imagegen.imagegen import ImageGen
from domains.text.textgen import TextGen
from models.llms import text_model
from typing import List, Optional
from rich.console import Console
from db import database


class StartRequest(BaseModel):
    concept: str
    domain: str


class RegenerateRequest(BaseModel):
    design_space: DesignSpace | None = None


class GenerationResponse(BaseModel):
    design_space: DesignSpace
    generations: List[Example]


class DomainResponse(BaseModel):
    name: str
    display_name: str


class Server:
    def __init__(
        self,
        domains: List[Domain],
        n: int,
        model: str = text_model,
        console: Console = None,
    ):
        self.app = FastAPI()
        self.domains = domains
        self.n = n
        self.model = model
        self.console = console

        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))

        self.static_dir = Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        self.app.mount(
            "/static", StaticFiles(directory=str(self.static_dir)), name="static"
        )
        for domain in self.domains:
            custom_scripts_path = domain.scripts_path
            self.app.mount(
                f"/{domain.name}",
                StaticFiles(directory=str(Path(custom_scripts_path).parent)),
                name=f"{domain.name}",
            )

        self.app.get("/")(self.start_page)
        self.app.get("/generation/{session_id}")(self.generation_page)

        #################################################################
        self.app.get("/api/domains")(self.get_domains)
        self.app.post("/api/generate")(self.generate)
        self.app.get("/api/generation/{session_id}")(self.get_generation)
        self.app.post("/api/generation/{session_id}/regenerate")(self.regenerate)

        # ------------------------------------------------------------------
        # Ablation routes
        # ------------------------------------------------------------------
        self.app.get("/ablation")(self.ablation_start_page)
        self.app.get("/ablation/{ablation_id}")(self.ablation_generation_page)
        self.app.get("/ablation-completed")(self.ablation_completed_page)

        self.app.post("/api/ablation/create")(self.create_ablation)
        self.app.get("/api/ablation/{ablation_id}")(self.get_ablation)
        self.app.post("/api/ablation/{ablation_id}/regenerate")(
            self.ablation_regenerate
        )
        self.app.post("/api/ablation/{ablation_id}/next")(self.ablation_next)

        # ------------------------------------------------------------------
        # Tutorial route
        # ------------------------------------------------------------------
        self.app.get("/tutorial")(self.tutorial_page)

    #################################################################
    # HTML endpoints
    #################################################################

    async def start_page(self, request: Request):
        return self.templates.TemplateResponse(
            "index.html",
            {"request": request},
        )

    async def generation_page(self, request: Request, session_id: str):
        session = database.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        domain = next((d for d in self.domains if d.name == session["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        custom_scripts_path = domain.scripts_path

        return self.templates.TemplateResponse(
            "generated.html",
            {
                "request": request,
                "domain_name": domain.display_name,
                "scripts_path": os.path.join(
                    f"/{domain.name}", custom_scripts_path.split("/")[-1]
                ),
                "concept": session["concept"],
                "session_id": session_id,
            },
        )

    async def tutorial_page(self, request: Request):
        """Render the interactive tutorial page that walks new users through the
        exploration workflow. The page itself is kept intentionally static – it
        explains the four-step loop and links back to the home page so users
        can try it themselves."""

        return self.templates.TemplateResponse(
            "tutorial.html",
            {"request": request},
        )

    #################################################################
    # API endpoints
    #################################################################

    async def get_domains(self) -> List[DomainResponse]:
        return [
            DomainResponse(name=d.name, display_name=d.display_name)
            for d in self.domains
        ]

    async def generate(self, request: StartRequest) -> RedirectResponse:
        domain = next((d for d in self.domains if d.name == request.domain), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        # Create new session
        session_id = database.create_session(request.concept, request.domain)

        # Redirect to generation page
        return {"url": f"/generation/{session_id}"}

    async def get_generation(self, session_id: str) -> GenerationResponse:
        session = database.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        domain = next((d for d in self.domains if d.name == session["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        # If no design space exists, create one
        if not session["current_design_space"]:
            design_space = DesignSpace.create(session["concept"], domain.display_name)
            design_space.explore_new_axis()
            design_space.fill()

            generations = generate(
                session["concept"],
                design_space,
                domain=domain,
                n=self.n,
                model=self.model,
                console=self.console,
            )
            database.update_session(session_id, design_space, generations)
        else:
            design_space = DesignSpace.model_validate_json(
                session["current_design_space"]
            )

            generations = (
                [
                    Example.model_validate_json(gen)
                    for gen in session["generations"][-1]["generations"]
                ]
                if session["generations"]
                else []
            )

        return GenerationResponse(design_space=design_space, generations=generations)

    async def regenerate(
        self, session_id: str, request: RegenerateRequest
    ) -> GenerationResponse:
        session = database.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        domain = next((d for d in self.domains if d.name == session["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        # Use provided design space or current one
        design_space = request.design_space or session["current_design_space"]
        if not design_space:
            raise HTTPException(status_code=404, detail="No design space found")

        generations = generate(
            session["concept"],
            design_space,
            domain=domain,
            n=self.n,
            model=self.model,
            console=self.console,
        )

        # Update session with new generations
        database.update_session(session_id, design_space, generations)

        return GenerationResponse(design_space=design_space, generations=generations)

    # ------------------------------------------------------------------
    # Ablation handlers
    # ------------------------------------------------------------------

    # Constants for ablation configuration
    ABLATION_PROMPTS: list[str] = [
        "A futuristic city at dusk with flying cars",
        "A serene beach sunrise with palm trees",
        "A steampunk-inspired airship over clouds",
        "A neon-lit cyberpunk alley at night",
        "A majestic dragon soaring above mountains",
        "A close-up of a dewdrop on a leaf",
        "A retro 80s style arcade room",
        "An elegant ballet dancer mid-jump",
        "A photorealistic red apple on marble",
        "A vibrant coral reef teeming with fish",
        "A snow-covered cabin in a forest",
        "A mystical portal in an ancient ruin",
        "A minimalist black and white spiral",
        "A cozy coffee shop interior",
        "A golden retriever wearing sunglasses",
        "A high-speed race car drifting",
        "A whimsical floating island landscape",
        "A microscopic view of a cell dividing",
    ]

    PROMPTS_PER_VARIANT = 1  # each ablation uses 6 prompts, 3 variants => 18 total

    ABLATION_VARIANTS = [
        {"name": "no_sort", "sort_results": False, "explore_all_axes": False},
        {"name": "all_axes_no_sort", "sort_results": False, "explore_all_axes": True},
        {"name": "full", "sort_results": True, "explore_all_axes": False},
    ]

    # ---------------- HTML ----------------

    async def ablation_start_page(self, request: Request):
        """Page where the participant enters their name to begin the ablation."""
        return self.templates.TemplateResponse(
            "ablation_start.html", {"request": request}
        )

    async def ablation_generation_page(self, request: Request, ablation_id: str):
        ablation = database.get_ablation(ablation_id)
        if not ablation:
            raise HTTPException(status_code=404, detail="Ablation not found")

        # Derive current prompt and variant label
        variant_index = ablation.get("variant_index", 0)
        prompt_index = ablation.get("prompt_index", 0)
        if variant_index >= len(self.ABLATION_VARIANTS):
            return RedirectResponse("/ablation-completed")

        base_idx = variant_index * self.PROMPTS_PER_VARIANT
        prompt_idx = base_idx + prompt_index
        if prompt_idx >= len(ablation["prompts"]):
            # Not enough prompts left – treat as complete
            return RedirectResponse("/ablation-completed")
        current_prompt = ablation["prompts"][prompt_idx]
        variant_name = self.ABLATION_VARIANTS[variant_index]["name"]

        domain = next((d for d in self.domains if d.name == ablation["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found for ablation")

        custom_scripts_path = domain.scripts_path

        return self.templates.TemplateResponse(
            "ablation_generated.html",
            {
                "request": request,
                "ablation_id": ablation_id,
                "variant_name": variant_name,
                "variant_index": variant_index,
                "prompt_index": prompt_index,
                "total_variants": len(self.ABLATION_VARIANTS),
                "total_prompts": self.PROMPTS_PER_VARIANT,
                "concept": current_prompt,
                "domain_name": domain.display_name,
                "scripts_path": os.path.join(
                    f"/{domain.name}", custom_scripts_path.split("/")[-1]
                ),
            },
        )

    async def ablation_completed_page(self, request: Request):
        """Simple thank-you page shown after finishing the study."""
        return self.templates.TemplateResponse(
            "ablation_completed.html", {"request": request}
        )

    # ---------------- API ----------------

    class CreateAblationRequest(BaseModel):
        user_name: str
        domain: Optional[str] = "image"  # default domain

    async def create_ablation(self, request: CreateAblationRequest):
        domain_name = request.domain or "image"
        if not any(d.name == domain_name for d in self.domains):
            raise HTTPException(status_code=404, detail="Domain not found")

        # Shuffle prompts so each participant gets a random order
        prompts = self.ABLATION_PROMPTS.copy()
        import random

        random.shuffle(prompts)

        # Keep only as many prompts as needed (PROMPTS_PER_VARIANT * variants)
        prompts = prompts[: self.PROMPTS_PER_VARIANT * len(self.ABLATION_VARIANTS)]

        ablation_id = database.create_ablation(
            user_name=request.user_name, domain=domain_name, prompts=prompts
        )

        return {"url": f"/ablation/{ablation_id}"}

    async def get_ablation(self, ablation_id: str) -> GenerationResponse:
        """Returns the current generation for the ablation, creating it if needed."""
        ablation = database.get_ablation(ablation_id)
        if not ablation:
            raise HTTPException(status_code=404, detail="Ablation not found")

        variant_index = ablation.get("variant_index", 0)
        prompt_index = ablation.get("prompt_index", 0)

        # If finished all variants return empty
        if variant_index >= len(self.ABLATION_VARIANTS):
            raise HTTPException(status_code=400, detail="Ablation completed")

        variant_config = self.ABLATION_VARIANTS[variant_index]
        base_idx = variant_index * self.PROMPTS_PER_VARIANT
        prompt_idx = base_idx + prompt_index
        if prompt_idx >= len(ablation["prompts"]):
            raise HTTPException(status_code=400, detail="Ablation completed")
        current_prompt = ablation["prompts"][prompt_idx]

        domain = next((d for d in self.domains if d.name == ablation["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        # If no design space exists for this prompt, create & generate
        if not ablation.get("current_design_space"):
            design_space = DesignSpace.create(current_prompt, domain.display_name)

            # Determine exploration mode
            design_space.explore_new_axis()
            design_space.fill()

            generations = generate(
                current_prompt,
                design_space,
                domain=domain,
                n=self.n,
                model=self.model,
                console=self.console,
                sort_results=variant_config["sort_results"],
                explore_all_axes=variant_config["explore_all_axes"],
            )

            database.update_ablation_generation(
                ablation_id,
                variant_index,
                prompt_index,
                design_space,
                generations,
            )
        else:
            design_space = DesignSpace.model_validate_json(
                ablation["current_design_space"]
            )
            generations = (
                [
                    Example.model_validate_json(gen)
                    for gen in ablation["history"][-1]["generations"]
                ]
                if ablation.get("history")
                else []
            )

        return GenerationResponse(design_space=design_space, generations=generations)

    async def ablation_regenerate(
        self, ablation_id: str, request: RegenerateRequest
    ) -> GenerationResponse:
        ablation = database.get_ablation(ablation_id)
        if not ablation:
            raise HTTPException(status_code=404, detail="Ablation not found")

        variant_index = ablation.get("variant_index", 0)
        prompt_index = ablation.get("prompt_index", 0)

        # If participant already finished all variants, abort
        if variant_index >= len(self.ABLATION_VARIANTS):
            raise HTTPException(status_code=400, detail="Ablation completed")

        variant_config = self.ABLATION_VARIANTS[variant_index]

        domain = next((d for d in self.domains if d.name == ablation["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        design_space = request.design_space or ablation.get("current_design_space")
        if not design_space:
            raise HTTPException(status_code=404, detail="No design space found")
        if isinstance(design_space, str):
            design_space = DesignSpace.model_validate_json(design_space)

        base_idx = variant_index * self.PROMPTS_PER_VARIANT
        prompt_idx = base_idx + prompt_index
        if prompt_idx >= len(ablation["prompts"]):
            raise HTTPException(status_code=400, detail="Ablation completed")
        current_prompt = ablation["prompts"][prompt_idx]

        generations = generate(
            current_prompt,
            design_space,
            domain=domain,
            n=self.n,
            model=self.model,
            console=self.console,
            sort_results=variant_config["sort_results"],
            explore_all_axes=variant_config["explore_all_axes"],
        )

        database.update_ablation_generation(
            ablation_id, variant_index, prompt_index, design_space, generations
        )

        return GenerationResponse(design_space=design_space, generations=generations)

    async def ablation_next(self, ablation_id: str):
        """Advance to the next prompt / variant."""
        database.advance_ablation(
            ablation_id,
            total_variants=len(self.ABLATION_VARIANTS),
            total_prompts=self.PROMPTS_PER_VARIANT,
        )
        return {"status": "ok"}

    def run(self, reload: bool = False, port: int = 8000):
        uvicorn.run(self.app, host="0.0.0.0", port=port, reload=reload)


def parse_args():
    parser = argparse.ArgumentParser(description="Run FastAPI server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument(
        "--n", type=int, default=6, help="Number of layouts to generate"
    )
    parser.add_argument("--reload", action="store_true", help="Enable hot reload")
    parser.add_argument(
        "--data-dir", type=str, default="../.data", help="Data directory"
    )
    parser.add_argument("--model", type=str, default=text_model, help="Model to use")
    parser.add_argument("--cerebras", action="store_true", help="Use Cerebras model")
    return parser.parse_args()


def main():
    args = parse_args()
    console = Console()
    if args.cerebras:
        model = "cerebras"
    else:
        model = args.model

    domains = [
        ImageGen(data_dir=args.data_dir, console=console, model=model),
        TextGen(data_dir=args.data_dir, console=console, model=model),
        UIGen(data_dir=args.data_dir, console=console, model=model),
    ]

    server = Server(n=args.n, domains=domains, model=model)
    server.run(reload=False, port=args.port)


if __name__ == "__main__":
    main()
