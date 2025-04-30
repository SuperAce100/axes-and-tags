from domains.domain import Domain
from domains.dormroom.dormroom import DormRoom
import argparse
from rich.console import Console
from domains.imagegen.imagegen import ImageGen
from models.models import cerebras_model

# Initialize rich console
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description='Generate dorm room layouts using DSL')
    parser.add_argument('--data-dir', type=str, default='../.data', help='Directory containing data')
    parser.add_argument('--domain', type=str, default='imagegen', help='Domain to run')
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

    if args.cerebras:
        args.model = "cerebras"
        args.n = 3
        console.print(f"[dark_orange]Using {cerebras_model} on Cerebras 🚀[/dark_orange]")

    if args.domain == "dormroom":
        domain = DormRoom(args.data_dir, args.model, console)
    elif args.domain == "imagegen":
        domain = ImageGen(args.concept, args.data_dir, args.model, console)
    else:
        raise ValueError(f"Domain {args.domain} not supported")

    domain.run_experiment(args.n, args.n_examples, args.max_iterations)

if __name__ == "__main__":
    main()
