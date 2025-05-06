from rich.progress import track
from models.prompts import dsl_system_prompt, dsl_example_format, feedback_example_format, example_room, dsl_user_prompt
from models.models import llm_call, text_model
from lib.utils import parse_dsl
import os
import concurrent.futures


def collect_examples(examples_dir: str, n: int = 10):
    examples = ""
    if n == 0:
        return examples, []

    if n > len(os.listdir(examples_dir)):
        n = len(os.listdir(examples_dir))
        
    if len(os.listdir(examples_dir)) == 0:
        return examples, []
    
    all_files = [f for f in os.listdir(examples_dir) if f.endswith(".dsl")]
    file_names = [os.path.splitext(f)[0] for f in all_files]
    
    # Sort files by modification time, most recent first
    file_times = [(f, os.path.getmtime(os.path.join(examples_dir, f))) for f in all_files]
    file_times.sort(key=lambda x: x[1], reverse=True)
    
    # Take the n most recent files
    yaml_files = [f[0] for f in file_times[:n]]
    example_names = [os.path.splitext(f)[0] for f in yaml_files]

    for yaml_file in yaml_files:
        with open(os.path.join(examples_dir, yaml_file), "r") as file:
            yaml_content = file.read()

        example_concept = os.path.splitext(yaml_file)[0]

        formatted_example = dsl_example_format.format(
            concept=example_concept, example=yaml_content
        )

        examples += formatted_example

    return examples, example_names


def generate_dsl(examples: str, model: str = text_model, prompt: str = "Generate a layout for a single dorm room", temperature: float = 1):
    system_prompt = dsl_system_prompt.format(examples=examples, room_dimensions=example_room)
    user_prompt = dsl_user_prompt.format(concept=prompt)
    response = llm_call(system_prompt, user_prompt, model=model, temperature=temperature)
    return parse_dsl(response)


def generate_dsl_multiple(examples: str, n: int = 10, model: str = text_model, prompt: str = "Generate a layout for a single dorm room", temperature: float = 1.5):
    dsl_objects = []

    def generate_one():
        return generate_dsl(examples, model, prompt, temperature=temperature)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_one) for _ in range(n)]
        dsl_objects = [future.result() for future in track(concurrent.futures.as_completed(futures), total=n, description=f"[grey11]Generating [bold cyan]{n}[/bold cyan] dorm rooms[/grey11]", style="grey15")]

    return dsl_objects


def load_dsl_from_feedback(feedback_data: dict[str, list], examples_dir: str):
    examples_str = ""
    for filename, feedbacks in feedback_data.items():
        with open(os.path.join(examples_dir, filename), "r") as f:
            yaml = f.read()
            yaml = "layout:" + yaml.split("layout:")[1] if "layout:" in yaml else yaml
            examples_str += feedback_example_format.format(concept="Dorm Room", example=yaml, feedback="\n".join(feedbacks))

    return examples_str


def save_dsl(dsl_objects: list, output_dir: str):
    for i, yaml in enumerate(dsl_objects):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"dorm_room_{i}.dsl"), "w") as f:
            combined_yaml = example_room + "\n" + yaml
            f.write(combined_yaml)


def main():
    examples, example_names = collect_examples("dorm room", "examples")

    dsl_objects = generate_dsl_multiple(examples, 10, text_model, temperature=0.5)
    save_dsl(dsl_objects, "results/test-3")


if __name__ == "__main__":
    main() 