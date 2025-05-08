from domains.domain import Domain
from domains.dormroom.dormroom import DormRoom
import argparse
from rich.console import Console
from domains.imagegen.imagegen import ImageGen
from domains.svg.svg import SVGGen
from domains.threejs.threejs import ThreeJSGen
from domains.ui.ui import UIGen
from models.models import cerebras_model

# Initialize rich console
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description='Generate dorm room layouts using DSL')
    parser.add_argument('--data-dir', type=str, default='../.data', help='Directory containing data')
    parser.add_argument('--domain', type=str, default='threejs', help='Domain to run')
    parser.add_argument('--n', type=int, default=6, help='Number of layouts to generate')
    parser.add_argument('--n-examples', type=int, default=10, help='Number of examples to use')
    parser.add_argument('--model', type=str, default='openai/gpt-4.1', help='Model to use')
    parser.add_argument('--cerebras', action='store_true', help='Use Cerebras model')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum number of iterations')
    parser.add_argument('--concept', type=str, default='elephant', help='Concept to generate')
    return parser.parse_args()

def main():
    args = parse_args()
    console = Console()

    n_examples = args.n_examples
    n = args.n

    if args.cerebras:
        args.model = "cerebras"
        n = 3
        console.print(f"[dark_orange]Using {cerebras_model} on Cerebras 🚀[/dark_orange]")

    if args.domain == "dormroom":
        domain = DormRoom(args.data_dir, args.model, console)
    elif args.domain == "imagegen":
        n = args.n
        n_examples = 0
        domain = ImageGen(args.concept, args.data_dir, args.model, console)
    elif args.domain == "svg":
        n = args.n
        n_examples = 5
        domain = SVGGen(args.concept, args.data_dir, args.model, console)
    elif args.domain == "threejs":
        n = args.n
        n_examples = 5
        domain = ThreeJSGen(args.concept, args.data_dir, args.model, console)
    elif args.domain == "ui":
        n = args.n
        n_examples = 0
        domain = UIGen(args.concept, args.data_dir, args.model, console)
    else:
        raise ValueError(f"Domain {args.domain} not supported")

    domain.run_experiment(n, n_examples, args.max_iterations)

if __name__ == "__main__":
    main()
