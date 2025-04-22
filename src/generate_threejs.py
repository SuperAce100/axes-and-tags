from tqdm import tqdm
from models.prompts import threejs_system_prompt, threejs_user_prompt, examples_format, feedback_example_format
from models.models import llm_call
from lib.utils import parse_threejs
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
    all_files = [f for f in os.listdir(examples_dir) if f.endswith(".js")]
    file_names = [os.path.splitext(f)[0] for f in all_files]
    
    concept_embedding = model.encode([concept])[0]
    filename_embeddings = model.encode(file_names)
    
    similarities = np.dot(filename_embeddings, concept_embedding)
    top_indices = np.argsort(similarities)[-n:][::-1]
    svg_files = [all_files[i] for i in top_indices]
    example_names = [file_names[i] for i in top_indices]

    for svg_file in svg_files:
        with open(os.path.join(examples_dir, svg_file), "r") as file:
            svg_content = file.read()

        example_concept = os.path.splitext(svg_file)[0]

        formatted_example = examples_format.format(
            concept=example_concept, example=svg_content
        )

        examples += formatted_example

    return examples, example_names


def generate_threejs(concept: str, examples: str):
    system_prompt = threejs_system_prompt.format(examples=examples)
    user_prompt = threejs_user_prompt.format(concept=concept)
    response = llm_call(system_prompt, user_prompt)
    return parse_threejs(response)


def generate_threejs_multiple(concept: str, examples: str, n: int = 10):
    threejs_objects = []

    def generate_one():
        return generate_threejs(concept, examples)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one) for _ in range(n)]
        threejs_objects = [future.result() for future in tqdm(concurrent.futures.as_completed(futures), total=n, desc="Generating 3D Objects")]

    return threejs_objects


def load_threejs_from_feedback(concept: str, feedback_data: dict[str, list], examples_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(examples_dir, filename), "r") as f:
            js = f.read()
            examples_str += feedback_example_format.format(concept=concept, example=js, feedback=feedbacks)
    return examples_str


def save_threejs(concept: str, threejs_objects: list, output_dir: str):
    for i, js in enumerate(threejs_objects):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"{concept}_{i}.js"), "w") as f:
            f.write(js)


def main():
    concept = "cow"
    examples, example_names = collect_examples(concept, "examples")

    threejs_objects = generate_threejs_multiple(concept, examples, 10)
    save_threejs(concept, threejs_objects, "results/test-3")


if __name__ == "__main__":
    main() 