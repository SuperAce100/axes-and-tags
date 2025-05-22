import argparse
from rich.console import Console
from domains.imagegen.imagegen import ImageGen
from domains.text.textgen import TextGen
from domains.ui.ui import UIGen
from models.models import cerebras_model

# Initialize rich console
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description='Generate dorm room layouts using DSL')
    parser.add_argument('--data-dir', type=str, default='../.data', help='Directory containing data')
    parser.add_argument('--domain', type=str, default='imagegen', help='Domain to run')
    parser.add_argument('--n', type=int, default=6, help='Number of layouts to generate')
    parser.add_argument('--n-examples', type=int, default=10, help='Number of examples to use')
    parser.add_argument('--model', type=str, default='anthropic/claude-3.7-sonnet', help='Model to use')
    parser.add_argument('--cerebras', action='store_true', help='Use Cerebras model')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum number of iterations')
    parser.add_argument('--concept', type=str, default='elephant', help='Concept to generate')
    parser.add_argument('--input-file', type=str, default=None, help='Input file to use')
    parser.add_argument('--vary-initial', action='store_true', help='Vary the initial design space')
    return parser.parse_args()

def main():
    args = parse_args()
    console = Console()

    n_examples = args.n_examples
    n = args.n

    if args.input_file:
        with open(args.input_file, 'r') as f:
            args.concept += " \n\n\n" + f.read()

    if args.cerebras:
        args.model = "cerebras"
        n = 3
        console.print(f"[dark_orange]Using {cerebras_model} on Cerebras 🚀[/dark_orange]")

    if args.domain == "text":
        domain = TextGen(args.concept, args.data_dir, args.model, console)
        n = args.n
        n_examples = 0
    elif args.domain == "imagegen":
        n = args.n
        n_examples = 0
        domain = ImageGen(args.concept, args.data_dir, args.model, console)
    elif args.domain == "ui":
        n = args.n
        n_examples = 0
        domain = UIGen(args.concept, args.data_dir, args.model, console)
    else:
        raise ValueError(f"Domain {args.domain} not supported")

    domain.run_experiment(n, args.vary_initial, args.max_iterations)

if __name__ == "__main__":
    main()
