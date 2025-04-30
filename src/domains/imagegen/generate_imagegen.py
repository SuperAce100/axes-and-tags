import base64
import os
import json
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from models.models import llm_call, text_model as language_model
import fal_client
import concurrent.futures
from rich.progress import track
from domains.imagegen.prompts import image_gen_expand_system_prompt, image_gen_expand_user_prompt, image_gen_examples_format, image_gen_feedback_format

img_model = "fal-ai/flux/schnell"

def expand_prompt(concept: str, model: str = language_model, examples: str = "") -> str:
    return llm_call(image_gen_expand_user_prompt.format(concept=concept), system_prompt=image_gen_expand_system_prompt.format(examples=examples))

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


def generate_image(concept: str, examples: str, image_model: str = img_model, text_model: str = language_model):
    expanded_prompt = expand_prompt(concept, text_model, examples)
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    result = fal_client.subscribe(
        image_model,
        arguments={
            "prompt": expanded_prompt,
            # "image_size": {
            #     "width": 1024,
            #     "height": 1024
            # }
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    image_url = result['images'][0]['url']
    # metadata = {"time": result['timings']['inference'], "width": result['images'][0]['width'], "height": result['images'][0]['height']}
    return expanded_prompt, image_url


def generate_image_multiple(concept: str, examples: str, n: int, image_model: str = img_model, text_model: str = language_model):
    image_urls = []

    def generate_one():
        return generate_image(concept, examples, image_model, text_model)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one) for _ in range(n)]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=n, description=f"[grey11]Generating [bold cyan]{n}[/bold cyan] images[/grey11]", style="grey15")]
        prompts, image_urls = zip(*results)

    return prompts, image_urls


def load_image_from_feedback(concept: str, feedback_data: dict[str, list], examples_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(examples_dir, filename), "r") as f:
            prompt = json.load(f)["prompt"]
            examples_str += image_gen_feedback_format.format(concept=concept, example=prompt, feedback=feedbacks)
    return examples_str

def save_images(image_urls: list[str], prompts: list[str], path: str):
    for i, (image_url, prompt) in enumerate(zip(image_urls, prompts)):
        os.makedirs(path, exist_ok=True)
        response = requests.get(image_url)
        image_data = base64.b64encode(response.content).decode('utf-8').replace('"', '\\"')
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": image_data}, f)
            print(f"Saved image {i} to {path}")

def main():
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/imagegen/examples", 5)
    prompts, image_urls = generate_image_multiple(concept, examples, 5)

    save_images(image_urls, prompts, "../.data/imagegen/results")

if __name__ == "__main__":
    main()

