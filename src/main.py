from generate_threejs import generate_threejs_multiple, collect_examples, save_threejs, load_threejs_from_feedback
from lib.viewer.threejs_viewer import ThreeJSViewer
import argparse
import random
import time
import os
import tkinter as tk

def name_output_dir(concept: str, output_dir: str):
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"{output_dir}/{concept}_{timestamp}_{random_suffix}"

def parse_args():
    parser = argparse.ArgumentParser(description='Generate 3D objects using Three.js')
    parser.add_argument('--concept', type=str, required=True, help='Concept to generate')
    parser.add_argument('--style', type=str, default='blocky', help='Style of the objects')
    parser.add_argument('--examples-dir', type=str, default='examples', help='Directory containing examples')
    parser.add_argument('--output-dir', type=str, default='results', help='Directory to save results')
    parser.add_argument('--n', type=int, default=10, help='Number of objects to generate')
    parser.add_argument('--n-examples', type=int, default=10, help='Number of examples to use')
    return parser.parse_args()

def main():
    args = parse_args()
    concept = args.concept
    style = args.style

    examples_dir = os.path.join(".data", style, args.examples_dir)
    results_dir = os.path.join(".data", style, args.output_dir)

    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    examples, example_names = collect_examples(concept, examples_dir, args.n_examples)
    print(f"Collected {len(example_names)} examples for concept: {concept}: {', '.join(example_names)}")

    print(f"Generating {args.n} 3D objects for concept: {args.concept}")

    threejs_objects = generate_threejs_multiple(concept, examples, args.n)

    output_dir = name_output_dir(concept, results_dir)

    save_threejs(concept, threejs_objects, output_dir)

    print(f"Saved {len(threejs_objects)} 3D objects to {output_dir}")

    viewer = ThreeJSViewer(output_dir, examples_dir, concept, f"{concept.capitalize()} made with {args.n_examples} examples")
    feedback_data = viewer.run()

    if not feedback_data: return

    feedback_examples = load_threejs_from_feedback(concept, feedback_data, output_dir)

    print(f"Feedback examples: {feedback_examples}")

    threejs_objects = generate_threejs_multiple(concept, feedback_examples, args.n)

    output_dir = os.path.join(output_dir, "feedback")

    save_threejs(concept, threejs_objects, output_dir)

    print(f"Saved {len(threejs_objects)} 3D objects after reflection to {output_dir}")

    viewer = ThreeJSViewer(output_dir, examples_dir, concept, f"{concept.capitalize()} made with {args.n_examples} examples post reflection", port=8002)
    feedback_data = viewer.run()

if __name__ == "__main__":
    main()
