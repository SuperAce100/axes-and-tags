import base64
import os
import json
import numpy as np
from pydantic import BaseModel
import requests
from sentence_transformers import SentenceTransformer
from models.models import llm_call, text_model as language_model
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


def generate_ui_multiple(concept: str, examples: str, n: int, old_tags: list[str], text_model: str = language_model):
    ui_results = []
    prompts = []

    expanded_prompts = llm_call(ui_expand_user_prompt.format(concept=concept), system_prompt=ui_expand_system_prompt.format(examples=examples) + ui_expand_system_prompt_extend.format(n=n))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt, old_tags)
        ui_result = generate_ui(prompt, examples, text_model)
        return ui_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] UIs[/grey11]", style="grey15")]
        ui_results, tags = zip(*results)
        prompts, uis = zip(*ui_results)

    return prompts, uis, tags

def extract_tags(prompt: str, old_tags: list[str], model: str = language_model) -> list[str]:
    tags_xml = llm_call(ui_tags_format.format(prompt=prompt, old_tags=old_tags), model=model)
    tags = [tag.strip() for tag in tags_xml.split("<tag>")[1:] if tag.strip()]
    tags = [tag.split("</tag>")[0].strip() for tag in tags]
    return tags

def generate_insights(feedback: str, model: str = language_model) -> str:
    return llm_call(ui_insights_format.format(feedback=feedback), model=model)

def load_ui_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            data = json.load(f)
            examples_str += ui_feedback_format.format(concept=concept, example=data["prompt"] + ": \n" + data["data"], feedback=feedbacks)
    
    insights = generate_insights(examples_str)

    return examples_str + "\n Here is what you need to include in every future generation: \n" + insights

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
    prompts, ui_results, tags = generate_ui_multiple(concept, examples, 5)

    save_ui(ui_results, prompts, tags, "../.data/ui/results")

if __name__ == "__main__":
    main()

