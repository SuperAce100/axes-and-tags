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

def extract_tags(prompt: str, design_space: DesignSpace, model: str = text_model) -> list[Tag]:

    design_space_str = "\n".join([f"{axis.name}" for axis in design_space.axes if axis.status == "exploring" or axis.status == "unconstrained"])

    tags_xml = llm_call(extract_tags_prompt.format(prompt=prompt, design_space=design_space_str), model=model)  
    tags = []

    tags_parts = tags_xml.split("<tag")
    if len(tags_parts) > 1:
        for tag in tags_parts[1:]:
            if "</tag>" in tag:

                dimension_match = re.search(r'dimension="([^"]+)"', tag)
                tag_value = tag.split(">", 1)[1].split("</tag>", 1)[0].strip()
                if dimension_match:
                    dimension = dimension_match.group(1)
                    tags.append(Tag(dimension=dimension, value=tag_value.lower()))

    for axis in design_space.axes:
        if axis.value and not any(t.dimension == axis.name for t in tags):
            tags.append(Tag(dimension=axis.name, value=axis.value.lower()))

    return tags


def generate(concept: str, design_space: DesignSpace, domain: Domain, n: int, model: str = text_model, console: Console = None) -> List[Example]:
    
    explorations = design_space.explore(n)

    if console:
        console.print("Explorations:", style="dim")
        console.print(explorations, style="dim")

    def generate_one(concept: str, design_space: DesignSpace, exploration: str, model: str = text_model) -> Example:
        for axis in design_space.axes:
            if axis.status == "exploring":
                axis.value = exploration

        example = domain.generate_one(concept, design_space, model)
        tags = extract_tags(example.prompt, design_space, model)
        return Example(prompt=example.prompt, content=example.content, tags=tags)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one, concept, design_space, exploration, model) for exploration in explorations]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), description="[dim]Generating examples...[/dim]", total=n)]
    
    save_path = os.path.join(domain.data_dir, f"{concept.replace(' ', '_')}_{domain.display_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            existing_results = json.load(f)
        existing_results["history"].append({"design_space": design_space.model_dump(), "results": [result.model_dump() for result in results]})
    else:
        existing_results = {"history": [{"design_space": design_space.model_dump(), "results": [result.model_dump() for result in results]}]}

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



