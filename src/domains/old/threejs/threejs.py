import os
import random
import time
from domains.domain import Domain
from domains.threejs.threejs_viewer import ThreeJSViewer
from domains.threejs.generate_threejs import collect_examples, extract_tags, generate_threejs_multiple, generate_insights, load_models_from_feedback, save_models
from models.llms import text_model
from typing import List, Tuple, Dict
from rich.console import Console

class ThreeJSGen(Domain):
    def __init__(self, concept: str, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(name="threejs", display_name=concept, data_dir=data_dir, model=model, console=console)
        self.concept = concept

    def run_viewer(self, title: str, port: int, path: str, used_examples: List[str] = None) -> None:
        viewer = ThreeJSViewer(
            concept=self.concept,
            threejs_folder=path, 
            output_path=self.examples_dir, 
            title=title, 
            port=port, 
            console=self.console,
            used_examples=used_examples
        )
        return viewer.run()

    def generate_multiple(self, n: int, examples: str, old_tags: List[str]) -> List[str]:
        return generate_threejs_multiple(self.concept, examples, old_tags, n, model=self.model)

    def collect_examples(self, n: int) -> Tuple[str, List[str]]:
        return collect_examples(self.concept, self.examples_dir, n)

    def feedback_examples(self, feedback: Dict[str, List[str]], results_dir: str) -> str:
        return load_models_from_feedback(self.concept, feedback, results_dir)
    
    def extract_tags(self, prompt: str, old_tags: List[str]) -> List[str]:
        return extract_tags(prompt, old_tags, self.model)

    def generate_insights(self, feedback: str) -> str:
        return generate_insights(feedback, self.model)

    def name_output_dir(self) -> str:
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"{self.output_dir}/{self.concept}_{timestamp}_{random_suffix}"

    def save_result(self, results: List[Tuple[str, str]], path: str = None) -> str:
        if path is None:
            path = self.name_output_dir()
        
        models = [r for r in results[0]]
        tags = [r for r in results[1]]

        save_models(models, tags, path)
        return path
