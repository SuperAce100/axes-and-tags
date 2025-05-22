import os
import random
import time
from domains.domain import Domain
from domains.dormroom.dormroom_viewer import DormRoomViewer
from domains.dormroom.generate_dormroom import generate_dsl, generate_dsl_multiple, collect_examples, load_dsl_from_feedback, save_dsl
from models.llms import text_model
from typing import List, Tuple, Dict
from rich.console import Console

class DormRoom(Domain):
    def __init__(self, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(name="dormroom", data_dir=data_dir, model=model, console=console)

    def run_viewer(self, title: str, port: int, path: str) -> None:
        viewer = DormRoomViewer(
            dormroom_folder=path, 
            output_path=self.examples_dir, 
            title=title, 
            port=port, 
            console=self.console
        )
        return viewer.run()

    def generate(self, examples: str) -> str:
        return generate_dsl(examples, self.model, self.console)

    def generate_multiple(self, n: int, examples: str) -> List[str]:
        return generate_dsl_multiple(examples, n, self.model)

    def collect_examples(self, n: int) -> Tuple[str, List[str]]:
        return collect_examples(self.examples_dir, n)

    def feedback_examples(self, feedback: Dict[str, List[str]]) -> str:
        return load_dsl_from_feedback(feedback, self.examples_dir)

    def name_output_dir(self) -> str:
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"{self.output_dir}/dorm_room_{timestamp}_{random_suffix}"

    def save_result(self, results: List[str], path: str = None) -> str:
        if path is None:
            path = self.name_output_dir()
        save_dsl(results, path)
        return path
