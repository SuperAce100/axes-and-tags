import base64
from designspace import DesignSpace, Generation
from domains.domain import Domain
from models.llms import llm_call, text_model
from rich.console import Console

text_gen_expand_system_prompt = """
You are a helpful assistant that expands prompts for text generation.
You will be given a concept and a list of examples.
You will need to expand the concept into a more detailed prompt that will be used to generate text.
The expanded prompt should be more specific and detailed than the original concept.
"""

text_gen_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>

Here is a precise description of what needs to be constrained in your expanded prompt:
{design_space}
"""

def expand_prompt(concept: str, design_space: DesignSpace, model: str = text_model, examples: str = "") -> str:
    return llm_call(text_gen_expand_user_prompt.format(concept=concept, design_space=design_space, examples=examples), system_prompt=text_gen_expand_system_prompt, temperature=1, model=model)

def generate_text(concept: str, design_space: DesignSpace, text_model: str = text_model) -> Generation:
    prompt = expand_prompt(concept, design_space, text_model)
    result = llm_call(prompt, temperature=1, model=text_model)
    return Generation(prompt=prompt, content=result)

class TextGen(Domain):
    def __init__(self, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(
            name="text", 
            display_name="Text", 
            data_dir=data_dir, 
            model=model, 
            console=console, 
            scripts_path="domains/text/text_scripts.js")

    def generate_one(self, concept: str, design_space: DesignSpace, model: str = text_model) -> Generation:
        return generate_text(concept, design_space, text_model=model)
