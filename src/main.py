from generate_dormroom import generate_dsl_multiple, collect_examples, save_dsl, load_dsl_from_feedback
from lib.viewer.threejs_viewer import ThreeJSViewer
import argparse
import random
import time
import os
import tkinter as tk
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

# Initialize rich console
console = Console()

def name_output_dir(output_dir: str):
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"{output_dir}/dorm_room_{timestamp}_{random_suffix}"

def parse_args():
    parser = argparse.ArgumentParser(description='Generate dorm room layouts using DSL')
    parser.add_argument('--examples-dir', type=str, default='dormroom/examples', help='Directory containing examples')
    parser.add_argument('--output-dir', type=str, default='dormroom/results', help='Directory to save results')
    parser.add_argument('--n', type=int, default=6, help='Number of layouts to generate')
    parser.add_argument('--n-examples', type=int, default=10, help='Number of examples to use')
    parser.add_argument('--model', type=str, default='openai/gpt-4.1', help='Model to use')
    parser.add_argument('--prompt', type=str, default='Dorm Room', help='Prompt to use')
    parser.add_argument('--cerebras', action='store_true', help='Use Cerebras model')
    return parser.parse_args()

def main():
    args = parse_args()

    if args.cerebras:
        args.model = "cerebras"
        args.n = 3

    examples_dir = os.path.join(".data", args.examples_dir)
    results_dir = os.path.join(".data", args.output_dir)

    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print("\n\n")
    console.print(Rule(f"[bold blue]Starting Initial {args.prompt} Generation[/bold blue]", style="grey11", align="left"))
    
    examples, example_names = collect_examples(args.prompt, examples_dir, args.n_examples)
    console.print(f"[green]✓[/green] Collected {len(example_names)} examples for {args.prompt}: [grey11]{', '.join(example_names)}[/grey11]")

    dsl_objects = generate_dsl_multiple(examples, args.n, args.model, args.prompt)

    output_dir = name_output_dir(results_dir)

    save_dsl(dsl_objects, output_dir)

    console.print(f"[green]✓[/green] [grey11]Saved [bold]{len(dsl_objects)}[/bold] {args.prompt} layouts to {output_dir}[/grey11]")

    viewer = ThreeJSViewer(output_dir, examples_dir, f"{args.prompt}", f"{args.prompt} layouts made with {args.n_examples} examples", console=console)
    feedback_data = viewer.run()

    iteration = 1
    while True:

        if not feedback_data:
            break


        
        feedback_examples = load_dsl_from_feedback(feedback_data, output_dir)
        
        feedback_text = Text()
        for i, name in enumerate(feedback_data.keys()):
            feedback_text.append(f"{i}. {name}: ", style="white")
            feedback_text.append("\n".join(feedback_data[name]) + "\n", style="grey11")
        
        console.print(Panel(feedback_text, title=f"[blue]Feedback for iteration {iteration}[/blue]", border_style="blue"))

        console.print(f"[grey11]Generating new layouts based on feedback...[/grey11]")
        dsl_objects = generate_dsl_multiple(feedback_examples, args.n, args.model, args.prompt, temperature=0.3)
        output_dir = os.path.join(output_dir, f"feedback_{iteration}")

        save_dsl(dsl_objects, output_dir)
        console.print(f"[green]✓[/green] [grey11]Saved [bold]{len(dsl_objects)}[/bold] {args.prompt} layouts after reflection {iteration} to {output_dir}[/grey11]")

        viewer = ThreeJSViewer(output_dir, examples_dir, f"{args.prompt} Layouts", 
            f"{args.prompt} made with {args.n_examples} examples post reflection (iteration {iteration})", 
            port=8002 + iteration, console=console)
        feedback_data = viewer.run()
        
            
        iteration += 1
    
    console.print(Rule(f"[bold green]Process Complete[/bold green]", style="green", align="left"))

if __name__ == "__main__":
    main()
