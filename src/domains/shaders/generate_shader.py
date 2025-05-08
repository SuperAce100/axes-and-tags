import os
import json
import numpy as np
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from models.models import llm_call, text_model as language_model
import concurrent.futures
from rich.progress import track
from domains.shaders.prompts import *


def expand_prompt(concept: str, model: str = language_model, examples: str = "") -> str:
    return llm_call(shader_expand_user_prompt.format(concept=concept), system_prompt=shader_expand_system_prompt.format(examples=examples), temperature=2)

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

        formatted_example = shader_examples_format.format(
            concept=example_concept, example=prompt
        )

        examples += formatted_example

    return examples, example_names


def generate_shader(prompt: str, examples: str, text_model: str = language_model):
    result = llm_call(prompt, system_prompt=shader_system_prompt.format(examples=examples), model=text_model)
    result = result.split("<shader>")[1].split("</shader>")[0].strip()
    return prompt,result


def generate_shader_multiple(concept: str, examples: str, n: int, old_tags: list[str], text_model: str = language_model):
    shader_results = []
    prompts = []

    expanded_prompts = llm_call(shader_expand_user_prompt.format(concept=concept), system_prompt=shader_expand_system_prompt.format(examples=examples) + shader_expand_system_prompt_extend.format(n=n))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt, old_tags)
        shader_result = generate_shader(prompt, examples, text_model)
        return shader_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] Shaders[/grey11]", style="grey15")]
        shader_results, tags = zip(*results)
        prompts, shaders = zip(*shader_results)

    return prompts, shaders, tags

def extract_tags(prompt: str, old_tags: list[str], model: str = language_model) -> list[str]:
    tags_xml = llm_call(shader_tags_format.format(prompt=prompt, old_tags=old_tags), model=model)
    tags = [tag.strip() for tag in tags_xml.split("<tag>")[1:] if tag.strip()]
    tags = [tag.split("</tag>")[0].strip() for tag in tags]
    return tags

def generate_insights(feedback: str, model: str = language_model) -> str:
    return llm_call(shader_insights_format.format(feedback=feedback), model=model)

def load_shader_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            prompt = json.load(f)["prompt"]
            examples_str += shader_feedback_format.format(concept=concept, example=prompt, feedback=feedbacks)
    
    insights = generate_insights(examples_str)

    return examples_str + "\n Here is what you need to include in every future generation: \n" + insights

def save_shader(shader_results: list[str], prompts: list[str], tags: list[str], path: str):
    os.makedirs(path, exist_ok=True)
    
    def save_one(args):
        i, (shader, prompt, tag) = args
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": shader, "tags": tag}, f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(save_one, enumerate(zip(shader_results, prompts, tags))))


def main():
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/shaders/examples", 5)
    prompts, shader_results, tags = generate_shader_multiple(concept, examples, 5)

    save_shader(shader_results, prompts, tags, "../.data/shaders/results")

if __name__ == "__main__":
    main()

