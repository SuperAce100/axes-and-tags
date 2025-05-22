from collections.abc import Callable
import os
import random
import time
from domains.domain import Domain
from domains.ui.generate_ui import generate_ui_multiple, collect_examples, load_ui_from_feedback, save_ui, expand_prompt, extract_tags, generate_insights, get_design_space, update_design_space
from domains.ui.ui_viewer import UIViewer
from models.models import text_model
from typing import List, Tuple, Dict
from rich.console import Console

class UIGen(Domain):
    def __init__(self, concept: str, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(name="ui", display_name=concept, data_dir=data_dir, model=model, console=console)
        self.concept = concept

    def run_viewer(self, title: str, port: int, path: str, used_examples: List[str] = None, design_space: dict[str, tuple[str, str]] = None, update_design_space: Callable[[dict[str, tuple[str, str]], dict[str, list[str]]], dict[str, tuple[str, str]]] = None) -> None:
        viewer = UIViewer(
            concept=self.concept,
            ui_folder=path, 
            output_path=self.examples_dir, 
            title=title, 
            port=port, 
            console=self.console,
            used_examples=used_examples,
            design_space=design_space,
            update_design_space=update_design_space
        )
        return viewer.run()

    def generate_multiple(self, n: int, examples: str, old_tags: List[str], design_space: dict[str, tuple[str, str]]) -> List[str]:
        return generate_ui_multiple(self.concept, examples, n, old_tags, design_space, text_model=self.model)

    def collect_examples(self, n: int) -> Tuple[str, List[str]]:
        return collect_examples(self.concept, self.examples_dir, n)

    def feedback_examples(self, feedback: Dict[str, List[str]], results_dir: str, design_space: dict[str, tuple[str, str]]) -> str:
        return load_ui_from_feedback(self.concept, feedback, results_dir, design_space)
    
    def extract_tags(self, prompt: str, old_tags: List[str], design_space: dict[str, tuple[str, str]]) -> List[str]:
        return extract_tags(prompt, old_tags, design_space, self.model)

    def generate_insights(self, feedback: str, design_space: dict[str, tuple[str, str]]) -> str:
        return generate_insights(feedback, design_space, self.model)

    def get_design_space(self) -> dict[str, tuple[str, str]]:
        return get_design_space(self.concept, self.model)

    def update_design_space(self, design_space: dict[str, tuple[str, str]], feedback_data: dict[str, list[str]]) -> dict[str, tuple[str, str]]:
        return update_design_space(design_space, feedback_data, self.model)

    def name_output_dir(self) -> str:
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"{self.output_dir}/{self.concept}_{timestamp}_{random_suffix}"

    def save_result(self, results: List[Tuple[str, str]], path: str = None) -> str:
        if path is None:
            path = self.name_output_dir()
        
        prompts = [r for r in results[0]]
        ui_results = [r for r in results[1]]
        tags = [r for r in results[2]]

        save_ui(ui_results, prompts, tags, path)
        return path
