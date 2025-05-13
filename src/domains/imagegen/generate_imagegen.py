import base64
import re
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
from domains.imagegen.prompts import *
from typing import List, Tuple, Dict

img_model = "fal-ai/flux/schnell"

def expand_prompt(concept: str, model: str = language_model, examples: str = "") -> str:
    return llm_call(image_gen_expand_user_prompt.format(concept=concept), system_prompt=image_gen_expand_system_prompt.format(examples=examples), temperature=2)

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

        formatted_example = image_gen_examples_format.format(
            concept=example_concept, example=prompt
        )

        examples += formatted_example

    return examples, example_names


def generate_image(prompt: str, examples: str, image_model: str = img_model, text_model: str = language_model):
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    result = fal_client.subscribe(
        image_model,
        arguments={
            "prompt": prompt,
            "image_size": {
                "width": 1024,
                "height": 1024
            }
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    image_url = result['images'][0]['url']
    # metadata = {"time": result['timings']['inference'], "width": result['images'][0]['width'], "height": result['images'][0]['height']}
    return prompt, image_url


def generate_image_multiple(concept: str, examples: str, n: int, old_tags: list[str], design_space: Dict[str, Tuple[str, str]], image_model: str = img_model, text_model: str = language_model):
    image_urls = []
    prompts = []

    expanded_prompts = llm_call(image_gen_expand_user_prompt.format(concept=concept), system_prompt=image_gen_expand_system_prompt.format(examples=examples) + image_gen_expand_system_prompt_extend.format(n=n))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt, old_tags, design_space=design_space)
        image_result = generate_image(prompt, examples, image_model, text_model)
        return image_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] images[/grey11]", style="grey15")]
        image_results, tags = zip(*results)
        prompts, image_urls = zip(*image_results)

    return prompts, image_urls, tags

def extract_tags(prompt: str, old_tags: list[str], model: str = language_model, design_space: List[Tuple[str, str]] = None) -> list[str]:
    tags_xml = llm_call(image_gen_tags_format.format(prompt=prompt, old_tags=old_tags, design_space=design_space), model=model)
    tags = [tag.strip() for tag in tags_xml.split("<tag>")[1:] if tag.strip()]
    tags = [tag.split("</tag>")[0].strip() for tag in tags]
    return tags

def generate_insights(feedback: str, design_space: Dict[str, Tuple[str, str]], model: str = language_model) -> str:
    return llm_call(image_gen_insights_format.format(feedback=feedback, design_space=design_space), model=model)

def get_design_space(concept: str, model: str = language_model) -> Dict[str, Tuple[str, str]]:
    response = llm_call(image_gen_get_design_space_prompt.format(concept=concept), model=model)
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
    
def update_design_space(design_space: Dict[str, Tuple[str, str]], feedback_data: dict[str, List[str]], model: str = language_model) -> Dict[str, Tuple[str, str]]:
    response = llm_call(image_gen_update_design_space_prompt.format(design_space=design_space, feedback_data=feedback_data), model=model)
    for axis_entry in response.split("<axis")[1:]:
        if "</axis>" in axis_entry:
            name_match = re.search(r'name="([^"]+)"', axis_entry)
            if name_match:
                axis_name = name_match.group(1)
                axis_value = axis_entry.split(">", 1)[1].split("</axis>", 1)[0].strip()
                design_space[axis_name] = ("constrained" if axis_value else "unconstrained", axis_value)
    return design_space

def load_image_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str, design_space: dict[str, Tuple[str, str]]):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            prompt = json.load(f)["prompt"]
            examples_str += image_gen_feedback_format.format(concept=concept, example=prompt, feedback=feedbacks)
    
    insights = generate_insights(examples_str, design_space)

    return examples_str + "\n Here is what you need to include in every future generation: \n" + insights

def save_images(image_urls: list[str], prompts: list[str], tags: list[str], path: str):
    os.makedirs(path, exist_ok=True)
    
    def save_one(args):
        i, (image_url, prompt, tag) = args
        response = requests.get(image_url)
        image_data = base64.b64encode(response.content).decode('utf-8').replace('"', '\\"')
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": image_data, "tags": tag}, f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(save_one, enumerate(zip(image_urls, prompts, tags))))


def main():
    design_space = """
    <design_space>
    <axis>car_type=sports</axis>
    <axis>car_color=red</axis>
    <axis>background=</axis>
    </design_space>
    """
    feedback_data = """
    <feedback_data>
    <feedback>I like the urban background</feedback>
    <feedback>I like the city street</feedback>
    </feedback_data>
    """
    print(update_design_space(design_space, feedback_data))

if __name__ == "__main__":
    main()

