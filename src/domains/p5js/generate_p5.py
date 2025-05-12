import os
import json
import numpy as np
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from models.models import llm_call, text_model as language_model
import concurrent.futures
from rich.progress import track
from domains.p5js.prompts import *


def expand_prompt(concept: str, model: str = language_model, examples: str = "") -> str:
    return llm_call(p5js_expand_user_prompt.format(concept=concept), system_prompt=p5js_expand_system_prompt.format(examples=examples), temperature=2)

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

        formatted_example = p5js_examples_format.format(
            concept=example_concept, example=prompt
        )

        examples += formatted_example

    return examples, example_names


def generate_p5js(prompt: str, examples: str, text_model: str = language_model):
    result = llm_call(prompt, system_prompt=p5js_system_prompt.format(examples=examples), model=text_model)
    result = result.split("<p5js>")[1].split("</p5js>")[0].strip()
    return prompt,result


def generate_p5js_multiple(concept: str, examples: str, n: int, old_tags: list[str], text_model: str = language_model):
    p5js_results = []
    prompts = []

    expanded_prompts = llm_call(p5js_expand_user_prompt.format(concept=concept), system_prompt=p5js_expand_system_prompt.format(examples=examples) + p5js_expand_system_prompt_extend.format(n=n))


    expanded_prompts = [p.strip() for p in expanded_prompts.split("<prompt>")[1:] if p.strip()]
    expanded_prompts = [p.split("</prompt>")[0].strip() for p in expanded_prompts]

    def process_prompt(prompt):
        tags = extract_tags(prompt, old_tags)
        p5js_result = generate_p5js(prompt, examples, text_model)
        return p5js_result, tags

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_prompt, prompt) for prompt in expanded_prompts]
        results = [future.result() for future in track(concurrent.futures.as_completed(futures), total=len(expanded_prompts), description=f"[grey11]Generating [bold cyan]{len(expanded_prompts)}[/bold cyan] P5JS Sketches[/grey11]", style="grey15")]
        p5js_results, tags = zip(*results)
        prompts, p5js = zip(*p5js_results)

    return prompts, p5js, tags

def extract_tags(prompt: str, old_tags: list[str], model: str = language_model) -> list[str]:
    tags_xml = llm_call(p5js_tags_format.format(prompt=prompt, old_tags=old_tags), model=model)
    tags = [tag.strip() for tag in tags_xml.split("<tag>")[1:] if tag.strip()]
    tags = [tag.split("</tag>")[0].strip() for tag in tags]
    return tags

def generate_insights(feedback: str, model: str = language_model) -> str:
    return llm_call(p5js_insights_format.format(feedback=feedback), model=model)

def load_p5js_from_feedback(concept: str, feedback_data: dict[str, list], results_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(results_dir, filename), "r") as f:
            data = json.load(f)
            examples_str += p5js_feedback_format.format(concept=concept, example=data["prompt"] + "\n" + data["data"], feedback=feedbacks)
    
    insights = generate_insights(examples_str)

    return examples_str + "\n Here is what you need to include in every future generation: \n" + insights

def save_p5js(p5js_results: list[str], prompts: list[str], tags: list[str], path: str):
    os.makedirs(path, exist_ok=True)
    
    def save_one(args):
        i, (p5js, prompt, tag) = args
        with open(os.path.join(path, f"{i}.json"), "w") as f:
            json.dump({"prompt": prompt, "data": p5js, "tags": tag}, f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(save_one, enumerate(zip(p5js_results, prompts, tags))))


def main():
    concept = "elephant"
    examples, example_names = collect_examples(concept, "../.data/p5js/examples", 5)
    prompts, p5js_results, tags = generate_p5js_multiple(concept, examples, 5)

    save_p5js(p5js_results, prompts, tags, "../.data/p5js/results")

if __name__ == "__main__":
    main()

