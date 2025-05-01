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
from domains.imagegen.prompts import image_gen_expand_system_prompt, image_gen_expand_user_prompt, image_gen_examples_format, image_gen_feedback_format, image_gen_expand_system_prompt_extend, image_gen_insights_format

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


    expanded_prompts = llm_call(image_gen_expand_user_prompt.format(concept=concept), system_prompt=image_gen_expand_system_prompt.format(examples=examples) + image_gen_expand_system_prompt_extend.format(n=n), temperature=1.5)

    # print(image_gen_expand_system_prompt.format(examples=examples))

    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]


    def generate_one(prompt):
        return generate_image(prompt, examples, image_model, text_model)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] images[/grey11]", style="grey15")]
        prompts, image_urls = zip(*results)

    return prompts, image_urls


def load_image_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            prompt = json.load(f)["prompt"]
            examples_str += image_gen_feedback_format.format(concept=concept, example=prompt, feedback=feedbacks)
    
    insights = llm_call(image_gen_insights_format.format(feedback=examples_str), model="anthropic/claude-3.7-sonnet")

    print(examples_str)
    print(insights)

    return examples_str + insights

def save_images(image_urls: list[str], prompts: list[str], path: str):
    os.makedirs(path, exist_ok=True)
    
    def save_one(args):
        i, (image_url, prompt) = args
        response = requests.get(image_url)
        image_data = base64.b64encode(response.content).decode('utf-8').replace('"', '\\"')
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": image_data}, f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(save_one, enumerate(zip(image_urls, prompts))))


def main():
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/imagegen/examples", 5)
    prompts, image_urls = generate_image_multiple(concept, examples, 5)

    save_images(image_urls, prompts, "../.data/imagegen/results")

if __name__ == "__main__":
    main()

