import os
from typing import Callable, List, Dict, Tuple
from abc import ABC, abstractmethod
from lib.utils import pretty_name
from models.models import text_model
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

class Domain(ABC):
    def __init__(self, name: str, display_name: str, data_dir: str, model: str = text_model, console: Console = Console()):
        self.name = name
        self.display_name = display_name
        self.data_dir = data_dir
        self.model = model
        self.console = console
        self.examples_dir = os.path.join(data_dir, name, "examples")
        self.output_dir = os.path.join(data_dir, name, "results")
        os.makedirs(self.examples_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    @abstractmethod
    def run_viewer(self, title: str, port: int, path: str, used_examples: List[str] = None, design_space: Dict[str, Tuple[str, str]] = None, update_design_space: Callable[[Dict[str, Tuple[str, str]], Dict[str, List[str]]], Dict[str, Tuple[str, str]]] = None) -> Dict[str, List[str]]:
        """Run the viewer for this domain. Returns a dictionary of example names and their feedback."""
        pass

    @abstractmethod
    def generate_multiple(self, n: int, examples: str, old_tags: List[str], design_space: Dict[str, Tuple[str, str]]) -> List[str]:
        """Generate multiple examples. Returns a list of generated examples."""
        pass

    @abstractmethod
    def collect_examples(self, n: int) -> Tuple[str, List[str]]:
        """Collect examples for this domain. Returns a tuple of example names and their content."""
        pass

    @abstractmethod
    def feedback_examples(self, feedback: Dict[str, List[str]], results_dir: str, design_space: Dict[str, Tuple[str, str]]) -> str:
        """Apply feedback to examples. Returns the feedback as a string."""
        pass

    @abstractmethod
    def generate_insights(self, feedback: str, design_space: Dict[str, Tuple[str, str]]) -> Tuple[str, Dict[str, Tuple[str, str]]]:
        """Generate insights from feedback. Returns the insights as a string."""
        pass

    @abstractmethod
    def extract_tags(self, prompt: str, old_tags: List[str], design_space: Dict[str, Tuple[str, str]]) -> List[str]:
        """Extract tags from a prompt. Returns a list of tags."""
        pass

    @abstractmethod
    def name_output_dir(self) -> str:
        """Name the output directory."""
        pass

    @abstractmethod
    def save_result(self, results: List[str], path: str = None) -> str:
        """Save the result of the domain processing. Returns the path to the saved result."""
        pass

    @abstractmethod
    def get_design_space(self) -> Dict[str, Tuple[str, str]]:
        """Get the design space that is being explored by the domain.
        Returns a dictionary of (space, (status, value))
        """
        pass

    @abstractmethod
    def update_design_space(self, design_space: Dict[str, Tuple[str, str]], feedback_data: Dict[str, List[str]]) -> Dict[str, Tuple[str, str]]:
        """Get the design space that is being explored by the domain.
        Returns a dictionary of (space, (status("constrained", "random", or "explored"), value))
        """
        pass

    def run_experiment(self, n: int, n_examples: int, max_iterations: int = 10):
        self.console.print(Rule(f"[bold green]Starting initial {self.name} generation[/bold green]", style="green", align="left"))

        design_space = self.get_design_space()
        self.console.print(f"[grey11]Design space: {design_space}[/grey11]")

        objects = self.generate_multiple(n, design_space, [], design_space)

        self.console.print(objects, style="grey11")

        save_path = self.save_result(objects)

        self.console.print(f"[green]✓[/green] [grey11]Saved [bold]{len(objects)}[/bold] {self.display_name}s to {self.output_dir}[/grey11]")

        viewer_data = self.run_viewer(pretty_name(f"Generated {len(objects[0])} {self.display_name}"), 8002, save_path, design_space=design_space, update_design_space=self.update_design_space)

        feedback_data = viewer_data["feedback"]
        design_space = viewer_data["design_space"]

        tags = []
        for feedback_list in feedback_data.values():
            tags.extend(feedback_list)

        for i in range(max_iterations):
            if not feedback_data and design_space == design_space:
                break
                

            design_space = self.update_design_space(design_space, feedback_data)

            self.console.print(f"[grey11]Updated design space: {design_space}[/grey11]")

            feedback_examples, temp_design_space = self.feedback_examples(feedback_data, save_path, design_space)

            feedback_text = Text()
            feedback_text.append(feedback_examples, style="grey11")

            self.console.print(Panel(feedback_text, title=f"[blue]Feedback for iteration {i}[/blue]", border_style="blue"))

            self.console.print(f"[grey11]Generating new layouts based on feedback...[/grey11]")

            objects = self.generate_multiple(n, feedback_examples, tags, temp_design_space)

            save_path = self.save_result(objects, os.path.join(save_path, "feedback"))
            self.console.print(f"[green]✓[/green] [grey11]Saved [bold]{len(objects)}[/bold] {self.display_name}s after reflection {i} to {self.output_dir}[/grey11]")

            new_viewer_data = self.run_viewer(pretty_name(f"{self.display_name}s made with {len(feedback_data)} labels (iteration {i})"), 8003 + i, save_path, used_examples=feedback_data, design_space=temp_design_space, update_design_space=self.update_design_space)

            if not new_viewer_data["feedback"] and new_viewer_data["design_space"] == temp_design_space:
                break

            new_feedback_data = new_viewer_data["feedback"]
            design_space = new_viewer_data["design_space"]

            feedback_data = {f"../{k}": v for k, v in feedback_data.items()}
            feedback_data = {**feedback_data, **new_feedback_data}
            for v in new_feedback_data.values():
                tags.extend(v)
        
        self.console.print(Rule(f"[bold green]Done![/bold green]", style="green", align="left"))
