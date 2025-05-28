import os
from abc import ABC, abstractmethod
from designspace import Generation
from rich.console import Console
from models.llms import text_model
from designspace import DesignSpace


class Domain(ABC):
    def __init__(
        self,
        name: str,
        display_name: str,
        data_dir: str,
        model: str = text_model,
        scripts_path: str = "",
        console: Console = Console(),
    ):
        self.name = name
        self.display_name = display_name
        self.data_dir = os.path.join(data_dir, name)
        self.model = model
        self.scripts_path = scripts_path
        self.console = console

    @abstractmethod
    def generate_one(
        self, concept: str, design_space: DesignSpace, model: str = text_model
    ) -> Generation:
        pass
