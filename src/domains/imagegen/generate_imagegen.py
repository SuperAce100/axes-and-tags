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
from domains.imagegen.prompts import *

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


def generate_image_multiple(concept: str, examples: str, n: int, image_model: str = img_model, text_model: str = language_model):
    image_urls = []
    prompts = []

    expanded_prompts = llm_call(image_gen_expand_user_prompt.format(concept=concept), system_prompt=image_gen_expand_system_prompt.format(examples=examples) + image_gen_expand_system_prompt_extend.format(n=n))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt)
        image_result = generate_image(prompt, examples, image_model, text_model)
        return image_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] images[/grey11]", style="grey15")]
        image_results, tags = zip(*results)
        prompts, image_urls = zip(*image_results)

    return prompts, image_urls, tags

def extract_tags(prompt: str, model: str = language_model) -> list[str]:
    tags_xml = llm_call(image_gen_tags_format.format(prompt=prompt), model=model)
    tags = [tag.strip() for tag in tags_xml.split("<tag>")[1:] if tag.strip()]
    tags = [tag.split("</tag>")[0].strip() for tag in tags]
    return tags

def generate_insights(feedback: str, model: str = language_model) -> str:
    return llm_call(image_gen_insights_format.format(feedback=feedback), model=model)

def load_image_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            prompt = json.load(f)["prompt"]
            examples_str += image_gen_feedback_format.format(concept=concept, example=prompt, feedback=feedbacks)
    
    insights = generate_insights(examples_str)

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
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/imagegen/examples", 5)
    prompts, image_urls, tags = generate_image_multiple(concept, examples, 5)

    save_images(image_urls, prompts, tags, "../.data/imagegen/results")

if __name__ == "__main__":
    main()

