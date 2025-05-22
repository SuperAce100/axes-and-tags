from designspace import DesignSpace, Generation
from domains.domain import Domain
from domains.imagegen.generate_imagegen import generate_image
from models.llms import text_model
from rich.console import Console

class ImageGen(Domain):
    def __init__(self, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(
            name="image", 
            display_name="Image", 
            data_dir=data_dir, 
            model=model, 
            console=console, 
            scripts_path="domains/imagegen/image_scripts.js")

    def generate_one(self, concept: str, design_space: DesignSpace, model: str = text_model) -> Generation:
        return generate_image(concept, design_space, text_model=model)
