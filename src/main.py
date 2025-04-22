from generate_dormroom import generate_dsl_multiple, collect_examples, save_dsl, load_dsl_from_feedback
from lib.viewer.threejs_viewer import ThreeJSViewer
import argparse
import random
import time
import os
import tkinter as tk

def name_output_dir(output_dir: str):
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"{output_dir}/dorm_room_{timestamp}_{random_suffix}"

def parse_args():
    parser = argparse.ArgumentParser(description='Generate dorm room layouts using DSL')
    parser.add_argument('--examples-dir', type=str, default='.data/dormroom/examples', help='Directory containing examples')
    parser.add_argument('--output-dir', type=str, default='.data/dormroom/results', help='Directory to save results')
    parser.add_argument('--n', type=int, default=6, help='Number of layouts to generate')
    parser.add_argument('--n-examples', type=int, default=10, help='Number of examples to use')
    parser.add_argument('--model', type=str, default='openai/gpt-4.1-mini', help='Model to use')
    return parser.parse_args()

def main():
    args = parse_args()

    examples_dir = os.path.join(".data", args.examples_dir)
    results_dir = os.path.join(".data", args.output_dir)

    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    examples, example_names = collect_examples("dorm room", examples_dir, args.n_examples)
    print(f"Collected {len(example_names)} examples for dorm room layouts: {', '.join(example_names)}")

    print(f"Generating {args.n} dorm room layouts")

    dsl_objects = generate_dsl_multiple(examples, args.n, args.model)

    output_dir = name_output_dir(results_dir)

    save_dsl(dsl_objects, output_dir)

    print(f"Saved {len(dsl_objects)} dorm room layouts to {output_dir}")

    viewer = ThreeJSViewer(output_dir, examples_dir, "Dorm Room Layouts", f"Dorm room layouts made with {args.n_examples} examples")
    feedback_data = viewer.run()

    if not feedback_data: return

    iteration = 1
    while True:
        feedback_examples = load_dsl_from_feedback(feedback_data, output_dir)
        print(f"Feedback examples: {feedback_examples}")

        dsl_objects = generate_dsl_multiple(feedback_examples, args.n)
        output_dir = os.path.join(output_dir, f"feedback_{iteration}")

        save_dsl(dsl_objects, output_dir)
        print(f"Saved {len(dsl_objects)} dorm room layouts after reflection to {output_dir}")

        viewer = ThreeJSViewer(output_dir, examples_dir, "Dorm Room Layouts", 
            f"Dorm room layouts made with {args.n_examples} examples post reflection (iteration {iteration})", 
            port=8002 + iteration)
        feedback_data = viewer.run()
        
        if not feedback_data:
            break
            
        iteration += 1

if __name__ == "__main__":
    main()
