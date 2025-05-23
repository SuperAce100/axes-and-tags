import base64
import fal_client
import requests
from designspace import DesignSpace, Generation
from domains.domain import Domain
from models.llms import llm_call, text_model
from rich.console import Console

img_model = "fal-ai/flux/schnell"

image_gen_expand_system_prompt = """
You are a helpful assistant that expands prompts for image generation.
You will be given a concept and a list of examples.
You will need to expand the concept into a more detailed prompt that will be used to generate an image.
The expanded prompt should be more specific and detailed than the original concept.
"""

image_gen_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>

Here is a precise description of what needs to be constrained in your expanded prompt:
{design_space}
"""

def expand_prompt(concept: str, design_space: DesignSpace, model: str = text_model, examples: str = "") -> str:
    return llm_call(image_gen_expand_user_prompt.format(concept=concept, design_space=design_space, examples=examples), system_prompt=image_gen_expand_system_prompt, temperature=1, model=model)

def generate_image(concept: str, design_space: DesignSpace, image_model: str = img_model, text_model: str = text_model) -> Generation:
    prompt = expand_prompt(concept, design_space, text_model)

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    result = fal_client.subscribe(
        image_model,
        arguments={
            "prompt": prompt,
            "image_size": {
                "width": 512,
                "height": 512
            }
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    image_url = result['images'][0]['url']
    print(image_url)

    response = requests.get(image_url)
    image_data = response.content
    image_base64 = base64.b64encode(image_data).decode('utf-8').replace('"', '\\"')

    return Generation(prompt=prompt, content=image_base64)

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
