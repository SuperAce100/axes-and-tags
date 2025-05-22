from ast import Dict, List, Tuple
import base64
import os
import json
import re
import numpy as np
from pydantic import BaseModel
import requests
from sentence_transformers import SentenceTransformer
from models.llms import llm_call, text_model as language_model
import fal_client
import concurrent.futures
from rich.progress import track
from domains.ui.prompts import *


def expand_prompt(concept: str, model: str = language_model, examples: str = "") -> str:
    return llm_call(ui_expand_user_prompt.format(concept=concept), system_prompt=ui_expand_system_prompt.format(examples=examples), temperature=2)

def collect_examples(concept: str,examples_dir: str = "examples", n: int = 5) -> list[str]:
    examples = ""
    if n == 0:
        return examples, []

    if n > len(os.listdir(examples_dir)):
        n = len(os.listdir(examples_dir))
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    all_files = [f for f in os.listdir(examples_dir) if f.endswith(".json")]
    file_names = [os.path.splitext(f)[0] for f in all_files]

    if len(file_names) == 0:
        return examples, []
    
    concept_embedding = model.encode([concept])[0]
    filename_embeddings = model.encode(file_names)
    
    similarities = np.dot(filename_embeddings, concept_embedding)
    top_indices = np.argsort(similarities)[-n:][::-1]
    chosen_files = [all_files[i] for i in top_indices]
    example_names = [file_names[i] for i in top_indices]

    for chosen_file in chosen_files:
        with open(os.path.join(examples_dir, chosen_file), "r") as file:
            prompt = json.load(file)["prompt"]

        example_concept = os.path.splitext(chosen_file)[0].split("_")[0]

        formatted_example = ui_examples_format.format(
            concept=example_concept, example=prompt
        )

        examples += formatted_example

    return examples, example_names


def generate_ui(prompt: str, examples: str, text_model: str = language_model):
    result = llm_call(prompt, system_prompt=ui_system_prompt.format(examples=examples), model=text_model)
    result = result.split("<ui>")[1].split("</ui>")[0].strip()
    return prompt,result


def generate_ui_multiple(concept: str, examples: str, n: int, old_tags: list[str], design_space: dict[str, tuple[str, str]], text_model: str = language_model):
    ui_results = []
    prompts = []

    expanded_prompts = llm_call(ui_expand_user_prompt.format(concept=concept), system_prompt=ui_expand_system_prompt.format(examples=examples) + ui_expand_system_prompt_extend.format(n=n, design_space=design_space))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt, old_tags, design_space)
        ui_result = generate_ui(prompt, examples, text_model)
        return ui_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] UIs[/grey11]", style="grey15")]
        ui_results, tags = zip(*results)
        prompts, uis = zip(*ui_results)

    return prompts, uis, tags

def extract_tags(prompt: str, old_tags: list[tuple[str, str]], design_space: dict[str, tuple[str, str]], model: str = language_model) -> list[tuple[str, str]]:
    tags_xml = llm_call(ui_tags_format.format(prompt=prompt, old_tags=old_tags, design_space=design_space), model=model)
    tags = []
    # Parse the tags XML format
    tags_parts = tags_xml.split("<tag")
    if len(tags_parts) > 1:
        for tag in tags_parts[1:]:
            if "</tag>" in tag:
                # Extract dimension and tag value
                dimension_match = re.search(r'dimension="([^"]+)"', tag)
                tag_value = tag.split(">", 1)[1].split("</tag>", 1)[0].strip()
                if dimension_match:
                    dimension = dimension_match.group(1)
                    tags.append((dimension, tag_value))
    return tags

def generate_insights(feedback: str, design_space: dict[str, tuple[str, str]], model: str = language_model) -> tuple[str, dict[str, tuple[str, str]]]:
    response = llm_call(ui_temp_design_space_format.format(feedback=feedback, design_space=design_space), model=model)
    # Parse the design space XML format
    temp_design_space = response.split("<design_space>")[1].split("</design_space>")[0].strip()
    
    # Extract axis information
    design_space_updates = {}
    for axis_line in temp_design_space.strip().split('\n'):
        if '<axis' in axis_line and '</axis>' in axis_line:
            name_match = re.search(r'name="([^"]+)"', axis_line)
            status_match = re.search(r'status="([^"]+)"', axis_line)
            if name_match:
                axis_name = name_match.group(1)
                axis_value = axis_line.split(">", 1)[1].split("</axis>", 1)[0].strip()
                design_space_updates[axis_name] = (status_match.group(1) if status_match else "unconstrained", axis_value)

    print(design_space_updates)

    design_space_string = ""
    constrained_string = ""
    exploring_string = ""
    for axis_name, (status, value) in design_space_updates.items():
        if status == "constrained" or status == "unconstrained":
            constrained_string += f"{axis_name}={value}\n"
        elif status == "exploring":
            exploring_string += f"{axis_name}\n"

    design_space_string = f"Constrained: {constrained_string}\nAreas to explore: {exploring_string}"

    return design_space_string, design_space_updates

def load_ui_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str, design_space: dict[str, tuple[str, str]]):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            data = json.load(f)
            examples_str += ui_feedback_format.format(concept=concept, example=data["prompt"] + ": \n" + data["data"], feedback=feedbacks)
    
    insights, temp_design_space = generate_insights(examples_str, design_space)

    return examples_str + "\n Here is what you need to include in every future generation: \n" + insights, temp_design_space

def get_design_space(concept: str, model: str = language_model) -> dict[str, tuple[str, str]]:
    response = llm_call(ui_get_design_space_prompt.format(concept=concept), model=model)
    # Extract axes from the response, handling potential parsing errors
    design_space = {}
    axes_parts = response.split("<axis>")
    if len(axes_parts) > 1:
        for axis in axes_parts[1:]:
            if "</axis>" in axis:
                axis_name = axis.split("</axis>")[0].strip()
                design_space[axis_name] = ("unconstrained", "")
            else:
                continue
    return design_space
    
def update_design_space(design_space: dict[str, tuple[str, str]], feedback_data: dict[str, list[str]], model: str = language_model) -> dict[str, tuple[str, str]]:
    response = llm_call(ui_update_design_space_prompt.format(design_space=design_space, feedback_data=feedback_data), model=model)
    for axis_entry in response.split("<axis")[1:]:
        if "</axis>" in axis_entry:
            name_match = re.search(r'name="([^"]+)"', axis_entry)
            status_match = re.search(r'status="([^"]+)"', axis_entry)
            if name_match:
                axis_name = name_match.group(1)
                axis_value = axis_entry.split(">", 1)[1].split("</axis>", 1)[0].strip()
                design_space[axis_name] = (status_match.group(1) if status_match else "unconstrained", axis_value)
    return design_space

def save_ui(ui_results: list[str], prompts: list[str], tags: list[str], path: str):
    os.makedirs(path, exist_ok=True)
    
    def save_one(args):
        i, (ui, prompt, tag) = args
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": ui, "tags": tag}, f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(save_one, enumerate(zip(ui_results, prompts, tags))))


def main():
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/ui/examples", 5)
    design_space = get_design_space(concept)
    prompts, ui_results, tags = generate_ui_multiple(concept, examples, 5, [], design_space)

    save_ui(ui_results, prompts, tags, "../.data/ui/results")

if __name__ == "__main__":
    main()

