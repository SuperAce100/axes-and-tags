import os
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, StreamingResponse
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
from datetime import datetime
from io import BytesIO
import random

# Matplotlib is an optional dependency used only for rendering the generation
# history figure. Importing it in a try/except ensures the server can still
# start even if the library is not yet installed (e.g. during cold starts) and
# keeps static analysers from flagging unresolved imports.
try:
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.patches import Rectangle, FancyBboxPatch  # type: ignore
    import matplotlib.font_manager as fm  # type: ignore

    # ------------------------------------------------------------------
    # Set up custom font
    # ------------------------------------------------------------------
    font_path = Path(__file__).parent / "static" / "fonts" / "Inter-Medium.ttf"
    font_prop = fm.FontProperties(fname=str(font_path))
except ModuleNotFoundError:  # pragma: no cover – handled at runtime
    plt = None  # type: ignore
    Rectangle = None  # type: ignore


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

        # ------------------------------------------------------------------
        # Figure route: visualize the full generation history as an image
        # ------------------------------------------------------------------
        self.app.get("/generation/{session_id}/figure")(self.generation_figure)

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

        # ------------------------------------------------------------------
        # Ablation viewer routes (read-only replay)
        # ------------------------------------------------------------------
        self.app.get("/ablation-viewer/{ablation_id}")(self.ablation_viewer_page)
        self.app.get("/api/ablation/{ablation_id}/history")(self.get_ablation_history)

        # ------------------------------------------------------------------
        # Ablations overview page
        # ------------------------------------------------------------------
        self.app.get("/ablations")(self.ablations_overview_page)

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
        "A car",
        "A dog",
        "A helmet",
        "A house",
        "A living room",
        "A kitchen",
        "A bedroom",
        "A desk setup",
        "A flower",
        "A beach",
        "A mountain",
        "A city skyline",
        "A cat",
        "A coffee shop",
        "A jacket",
        "A race car",
        "A floating island",
        "A bird",
    ]

    PROMPTS_PER_VARIANT = 4  # each ablation uses 6 prompts, 3 variants => 18 total

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

    async def ablation_viewer_page(self, request: Request, ablation_id: str):
        """Read-only page to replay an ablation run after completion."""
        ablation = database.get_ablation(ablation_id)
        if not ablation:
            raise HTTPException(status_code=404, detail="Ablation not found")

        domain = next((d for d in self.domains if d.name == ablation["domain"]), None)
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")

        custom_scripts_path = domain.scripts_path

        return self.templates.TemplateResponse(
            "ablation_viewer.html",
            {
                "request": request,
                "ablation_id": ablation_id,
                "user_name": ablation.get("user_name", ""),
                "scripts_path": os.path.join(
                    f"/{domain.name}", custom_scripts_path.split("/")[-1]
                ),
            },
        )

    async def get_ablation_history(self, ablation_id: str):
        """Return the full, parsed generation history for a finished ablation."""
        import json

        ablation = database.get_ablation(ablation_id)
        if not ablation:
            raise HTTPException(status_code=404, detail="Ablation not found")

        history = ablation.get("history", [])
        parsed_history = []
        for record in history:
            # Parse stored JSON strings back into objects/dicts that can be sent over the wire
            design_space = json.loads(record["design_space"])
            generations = [json.loads(g) for g in record.get("generations", [])]
            parsed_history.append(
                {
                    "variant_index": record.get("variant_index"),
                    "prompt_index": record.get("prompt_index"),
                    "timestamp": record.get("timestamp"),
                    "design_space": design_space,
                    "generations": generations,
                }
            )

        return parsed_history

    async def ablations_overview_page(self, request: Request):
        """List all ablation runs with a preview image."""
        import json

        ablations = database.list_ablations()
        overview_items = []
        for record in ablations:
            sample_img = None
            if record.get("history"):
                first_gen = (
                    record["history"][0]["generations"][0]
                    if record["history"][0]["generations"]
                    else None
                )
                if first_gen:
                    try:
                        gen_obj = json.loads(first_gen)
                        sample_img = gen_obj.get("content")
                    except Exception:
                        sample_img = None
            overview_items.append(
                {
                    "id": record["id"],
                    "user_name": record.get("user_name", ""),
                    "created_at": (
                        datetime.fromisoformat(record["created_at"]).strftime(
                            "%Y-%m-%d %H:%M"
                        )
                        if record.get("created_at")
                        else ""
                    ),
                    "sample_img": (
                        f"data:image/png;base64,{sample_img}" if sample_img else None
                    ),
                }
            )

        return self.templates.TemplateResponse(
            "ablations_overview.html",
            {"request": request, "ablations": overview_items},
        )

    async def generation_figure(self, session_id: str):
        """Return a PNG image visualising the full generation history.

        The figure shows each generation step as a row of grey squares. The text
        inside the square corresponds to the value explored for the axis that
        was marked as "exploring" during that step. Between rows an arrow and
        a caption "Exploring <axis>" indicate which design dimension was being
        iterated on.
        """
        if plt is None or Rectangle is None:  # Matplotlib missing – user must install
            raise HTTPException(
                status_code=500,
                detail="matplotlib is required for this endpoint. Add it to your environment.",
            )

        session = database.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        history = session.get("generations", [])
        if not history:
            raise HTTPException(status_code=404, detail="No generation history found")

        # Each row: axis name, list of (label, image_b64 | None)
        rows: list[tuple[str, list[tuple[str, str | None]], str | None]] = []
        max_cols = 0

        total_steps = len(history)
        for idx, step in enumerate(history):
            # Reconstruct DesignSpace to find the currently explored axis
            design_space_json = step.get("design_space")
            try:
                design_space = DesignSpace.model_validate_json(design_space_json)
            except Exception:
                continue  # skip malformed entries

            exploring_axis = next(
                (axis for axis in design_space.axes if axis.status == "exploring"),
                None,
            )
            axis_name = exploring_axis.name if exploring_axis else ""

            # Decode examples and extract tag values for the exploring axis
            examples_json = step.get("generations", [])
            example_objs = [
                Example.model_validate_json(ej) for ej in examples_json if ej
            ]

            cells: list[tuple[str, str | None]] = []
            for ex in example_objs:
                match = next(
                    (t.value for t in ex.tags if t.dimension == axis_name),
                    None,
                )
                label = match if match is not None else ""
                image_b64: str | None = ex.content if ex.content else None
                cells.append((label, image_b64))

            # Determine which value was selected for this axis by looking ahead
            selected_value: str | None = None
            for later_step in history[idx + 1 :]:
                later_ds_json = later_step.get("design_space")
                try:
                    later_ds = DesignSpace.model_validate_json(later_ds_json)
                except Exception:
                    continue
                later_axis = next(
                    (a for a in later_ds.axes if a.name == axis_name), None
                )
                if later_axis and later_axis.value:
                    selected_value = later_axis.value.lower()
                    break

            max_cols = max(max_cols, len(cells))

            # If this is the last row and no value was selected, choose one randomly
            is_last_row = idx == total_steps - 1
            if is_last_row and selected_value is None and cells:
                selected_value = random.choice(cells)[0].lower()

            rows.append((axis_name, cells, selected_value))

        # --------------------------
        # Draw the figure
        # --------------------------
        # ------------------------------------------------------------------
        # Global aesthetic tweaks
        # ------------------------------------------------------------------
        plt.rcParams["font.family"] = ["Inter", "DejaVu Sans", "sans-serif"]

        COL_SPACING = 2.0  # horizontal space between left edges of squares
        LEFT_MARGIN = 0.1  # slight shift right to avoid clipping
        ROW_SPACING = 2.7  # vertical space between successive rows
        SQUARE_SIZE = 1.9
        BOTTOM_MARGIN = -0.9

        fig_width = LEFT_MARGIN + max_cols * COL_SPACING
        fig_height = len(rows) * ROW_SPACING + BOTTOM_MARGIN
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, fig_width)
        ax.set_ylim(
            -0.2, fig_height + 0.2
        )  # slight negative bottom to reduce whitespace
        ax.set_axis_off()

        from base64 import b64decode  # local import to avoid overhead if not needed
        from PIL import Image  # pillow dependency

        for row_idx, (axis_name, cells, selected_value) in enumerate(rows):
            # y coordinate of the top-left corner of the row (invert because matplotlib's origin is bottom-left)
            y = fig_height - (row_idx + 1) * ROW_SPACING + (ROW_SPACING - SQUARE_SIZE)

            # Determine which column is selected (if any)
            selected_col_idx: int | None = None
            if selected_value is not None:
                for c_idx, (lbl, _img) in enumerate(cells):
                    if lbl.lower() == selected_value.lower():
                        selected_col_idx = c_idx
                        break

            for col_idx, (label, image_b64) in enumerate(cells):
                x = LEFT_MARGIN + col_idx * COL_SPACING
                # Check if this cell's label matches the selected value
                is_selected = (
                    selected_value is not None
                    and label.lower() == selected_value.lower()
                )

                # ------------------------------------------------------------------
                # Render image and rounded-corner border together
                # ------------------------------------------------------------------

                # Create rounded box that doubles as border and clipping mask
                rect = FancyBboxPatch(
                    (x, y),
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                    facecolor="none",
                    edgecolor="#2ecc71" if is_selected else "black",
                    linewidth=3.0 if is_selected else 1.0,
                    boxstyle="round,pad=0.02,rounding_size=0.15",
                    zorder=2,
                )
                ax.add_patch(rect)

                # Render image clipped to the rounded rectangle
                img_bytes = b64decode(image_b64)
                img = Image.open(BytesIO(img_bytes))
                im = ax.imshow(
                    img,
                    extent=(
                        x - 0.01,
                        x + SQUARE_SIZE + 0.01,
                        y - 0.01,
                        y + SQUARE_SIZE + 0.01,
                    ),
                    zorder=1,
                )
                im.set_clip_path(rect)

                # Overlay label on image with semi-transparent background
                ax.text(
                    x + SQUARE_SIZE / 2,
                    y + 0.2,
                    label,
                    ha="center",
                    va="bottom",
                    fontsize=12,
                    color="white",
                    fontweight="bold",
                    bbox=dict(
                        facecolor="black",
                        alpha=0.6,
                        pad=8,
                        edgecolor="none",
                        boxstyle="round,pad=0.75,rounding_size=1",
                    ),
                    zorder=3,
                )

            # ------------------------------------------------------------------
            # Row heading: "Exploring <axis>"
            # ------------------------------------------------------------------
            ax.text(
                LEFT_MARGIN + (max_cols * COL_SPACING) / 2,
                y + SQUARE_SIZE + 0.35,
                f"Exploring {axis_name.replace('_', ' ')}",
                ha="center",
                va="bottom",
                fontsize=14,
                fontproperties=font_prop,
                fontweight="bold",
                bbox=dict(
                    facecolor="white",
                    alpha=1.0,
                    pad=4,
                    edgecolor="none",
                    boxstyle="round,pad=0.25,rounding_size=0.15",
                ),
                zorder=4,
            )

            # ------------------------------------------------------------------
            # Arrow pointing to the next row (except for the last row)
            # ------------------------------------------------------------------
            if row_idx < len(rows) - 1:
                if selected_col_idx is not None:
                    arrow_x = (
                        LEFT_MARGIN + selected_col_idx * COL_SPACING + SQUARE_SIZE / 2
                    )
                else:
                    arrow_x = LEFT_MARGIN + (max_cols * COL_SPACING) / 2
                arrow_start_y = y - 0.1
                arrow_end_y = arrow_start_y - (ROW_SPACING - SQUARE_SIZE) + 0.2
                ax.annotate(
                    "",
                    xy=(arrow_x, arrow_end_y),
                    xytext=(arrow_x, arrow_start_y),
                    arrowprops=dict(arrowstyle="->", lw=1.5),
                    zorder=1,
                )

        fig.tight_layout()
        buf = BytesIO()
        fig.savefig(buf, format="pdf", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/pdf")

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
