import os
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

        self.app.get("/")(self.start_page)
        self.app.get("/generation/{session_id}")(self.generation_page)

        #########################################################
        self.app.get("/api/domains")(self.get_domains)
        self.app.post("/api/generate")(self.generate)
        self.app.get("/api/generation/{session_id}")(self.get_generation)
        self.app.post("/api/generation/{session_id}/regenerate")(self.regenerate)

    #########################################################
    # HTML endpoints
    #########################################################

    async def start_page(self, request: Request):
        return self.templates.TemplateResponse("index.html", {"request": request})

    async def generation_page(self, request: Request, session_id: str):
        session = database.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        domain = next((d for d in self.domains if d.name == session["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        custom_scripts_path = domain.scripts_path
        print(custom_scripts_path, domain)
        self.app.mount(
            "/custom",
            StaticFiles(directory=str(Path(custom_scripts_path).parent)),
            name="custom",
        )

        return self.templates.TemplateResponse(
            "generated.html",
            {
                "request": request,
                "domain_name": domain.display_name,
                "scripts_path": os.path.join(
                    "/custom", custom_scripts_path.split("/")[-1]
                ),
                "concept": session["concept"],
                "session_id": session_id,
            },
        )

    #########################################################
    # API endpoints
    #########################################################

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
