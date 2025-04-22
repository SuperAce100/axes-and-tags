from tqdm import tqdm
from models.prompts import dsl_system_prompt, dsl_example_format, examples_format, feedback_example_format
from models.models import llm_call, text_model
from lib.utils import parse_dsl
import os
import concurrent.futures
from sentence_transformers import SentenceTransformer
import numpy as np


def collect_examples(concept: str, examples_dir: str, n: int = 10):
    examples = ""
    if n == 0:
        return examples, []

    if n > len(os.listdir(examples_dir)):
        n = len(os.listdir(examples_dir))
        
    if len(os.listdir(examples_dir)) == 0:
        return examples, []
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    all_files = [f for f in os.listdir(examples_dir) if f.endswith(".dsl")]
    file_names = [os.path.splitext(f)[0] for f in all_files]
    
    print(file_names)
    
    concept_embedding = model.encode([concept])[0]
    filename_embeddings = model.encode(file_names)
    
    similarities = np.dot(filename_embeddings, concept_embedding)
    top_indices = np.argsort(similarities)[-n:][::-1]
    yaml_files = [all_files[i] for i in top_indices]
    example_names = [file_names[i] for i in top_indices]

    for yaml_file in yaml_files:
        with open(os.path.join(examples_dir, yaml_file), "r") as file:
            yaml_content = file.read()

        example_concept = os.path.splitext(yaml_file)[0]

        formatted_example = examples_format.format(
            concept=example_concept, example=yaml_content
        )

        examples += formatted_example

    return examples, example_names


def generate_dsl(examples: str, model: str = text_model, prompt: str = "Generate a layout for a single dorm room"):
    system_prompt = dsl_system_prompt.format(examples=examples)
    user_prompt = prompt
    response = llm_call(system_prompt, user_prompt, model=model)
    return parse_dsl(response)


def generate_dsl_multiple(examples: str, n: int = 10, model: str = text_model, prompt: str = "Generate a layout for a single dorm room"):
    dsl_objects = []

    def generate_one():
        return generate_dsl(examples, model, prompt)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one) for _ in range(n)]
        dsl_objects = [future.result() for future in tqdm(concurrent.futures.as_completed(futures), total=n, desc="Generating Room Layouts")]

    return dsl_objects


def load_dsl_from_feedback(feedback_data: dict[str, list], examples_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(examples_dir, filename), "r") as f:
            yaml = f.read()
            examples_str += feedback_example_format.format(concept="dorm room", example=yaml, feedback=feedbacks)
    return examples_str


def save_dsl(dsl_objects: list, output_dir: str):
    for i, yaml in enumerate(dsl_objects):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"dorm_room_{i}.dsl"), "w") as f:
            f.write(yaml)


def main():
    examples, example_names = collect_examples("dorm room", "examples")

    dsl_objects = generate_dsl_multiple(examples, 10, text_model)
    save_dsl(dsl_objects, "results/test-3")


if __name__ == "__main__":
    main() 