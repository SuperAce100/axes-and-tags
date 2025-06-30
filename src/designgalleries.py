import concurrent.futures
from datetime import datetime
import json
import os
from designspace import DesignSpace, Tag, Example
from domains.imagegen.imagegen import ImageGen
from models.llms import text_model, llm_call
from domains.domain import Domain
from typing import Dict, Tuple, List
from models.prompts import extract_tags_prompt
from rich.console import Console
import re
from rich.progress import track


def generate(
    concept: str,
    design_space: DesignSpace,
    domain: Domain,
    n: int,
    model: str = text_model,
    console: Console = None,
    *,
    sort_results: bool = True,
    explore_all_axes: bool = False,
) -> List[Example]:
    # ------------------------------------------------------------------
    # Decide how we obtain exploration variants depending on ablation mode
    # ------------------------------------------------------------------

    if explore_all_axes:
        # In this mode we want to explore all design axes simultaneously.
        # The existing DesignSpace.explore method only works with a single
        # axis marked as "exploring", so here we approximate multi-axis
        # exploration by generating n independent fills of the entire
        # design space.
        explorations = [f"exploration_{i}" for i in range(n)]  # dummy placeholders
    else:
        explorations = design_space.explore(n)

    if console:
        console.print("Explorations:", style="dim")
        console.print(explorations, style="dim")

    # If we are in the all-axes exploration mode we will perform a full space
    # fill for every generation rather than varying a single axis.
    def _prepare_design_space_for_all_axes():
        # Mark every axis as unconstrained so that `.fill()` assigns values.
        for axis in design_space.axes:
            axis.status = "unconstrained"
            axis.value = ""
        design_space.fill()

    def generate_one(
        concept: str,
        design_space: DesignSpace,
        exploration: str,
        model: str = text_model,
    ) -> Example:
        if explore_all_axes:
            _prepare_design_space_for_all_axes()
        else:
            for axis in design_space.axes:
                if axis.status == "exploring":
                    axis.value = exploration

        example = domain.generate_one(concept, design_space, model)
        exploring_axis = next(
            (axis for axis in design_space.axes if axis.status == "exploring"), None
        )
        tags = (
            [Tag(dimension=exploring_axis.name, value=exploration.lower())]
            if exploring_axis
            else []
        )
        return Example(prompt=example.prompt, content=example.content, tags=tags)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                generate_one, concept, design_space, exploration, model
            ): exploration
            for exploration in explorations
        }
        results = []
        for future in track(
            concurrent.futures.as_completed(futures),
            description="[dim]Generating examples...[/dim]",
            total=n,
        ):
            results.append((futures[future], future.result()))

        # Sort results by original exploration order if requested
        if sort_results and explorations:
            results.sort(key=lambda x: explorations.index(x[0]))
        # Strip exploration keys, keep only Example objects
        results = [r[1] for r in results]

    save_path = os.path.join(
        domain.data_dir,
        f"{concept.replace(' ', '_')}_{domain.display_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
    )
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            existing_results = json.load(f)
        existing_results["history"].append(
            {
                "design_space": design_space.model_dump(),
                "results": [result.model_dump() for result in results],
            }
        )
    else:
        existing_results = {
            "history": [
                {
                    "design_space": design_space.model_dump(),
                    "results": [result.model_dump() for result in results],
                }
            ]
        }

    if console:
        console.print(f"Saving results to {save_path}", style="dim")

    with open(save_path, "w") as f:
        json.dump(existing_results, f)

    if console:
        console.print(f"Results saved to {save_path}", style="dim")

    return results


if __name__ == "__main__":
    console = Console()
    domain = ImageGen(data_dir="../.data", console=console)
    concept = input("Enter a concept: ")
    design_space = DesignSpace.create(concept, domain.display_name)

    console.print("Generated design space:", style="dim")
    console.print(design_space, style="dim")

    design_space.explore_new_axis()

    console.print("Selected axis to explore:", style="dim")
    console.print(design_space, style="dim")

    design_space.fill()

    console.print("Filled design space:", style="dim")
    console.print(design_space, style="dim")

    generations = generate(concept, design_space, domain, 6, console=console)

    for generation in generations:
        print(generation.prompt)
        print(generation.tags)
