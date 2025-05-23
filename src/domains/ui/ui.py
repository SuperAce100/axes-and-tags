import base64
from designspace import DesignSpace, Generation
from domains.domain import Domain
from models.llms import llm_call, text_model
from rich.console import Console

ui_gen_expand_system_prompt = """
You are a helpful assistant that expands prompts that will be sent to a UI generation model.
You will be given a concept and a list of examples.
You will need to expand the concept into a more detailed prompt that will be used to generate UI designs.
The expanded prompt should be more specific and detailed than the original concept.
"""

ui_gen_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>

Here is a precise description of what needs to be constrained in your expanded prompt:
{design_space}
"""

ui_gen_system_prompt = """
You must generate a UI element based on a given prompt.

The UI must be wrapped in a <ui></ui> XML tag, like this:

<ui>
<!-- UI HERE -->
</ui>

The UI must be a valid HTML div element, and you should use Tailwind CSS classes to style it.

The outer level of the UI must be a div element, with the w-full and h-full classes, so it takes the full width and height of the container.

Make sure to follow every single instruction provided in the prompt carefully, and comment your code extensively.
"""

def expand_prompt(concept: str, design_space: DesignSpace, model: str = text_model, examples: str = "") -> str:
    return llm_call(ui_gen_expand_user_prompt.format(concept=concept, design_space=design_space, examples=examples), system_prompt=ui_gen_expand_system_prompt, temperature=1, model=model)

def generate_ui(concept: str, design_space: DesignSpace, text_model: str = text_model) -> Generation:
    prompt = expand_prompt(concept, design_space, text_model)
    result = llm_call(prompt, model="anthropic/claude-3-7-sonnet", system_prompt=ui_gen_system_prompt)
    result = result.split("<ui>")[1].split("</ui>")[0].strip()
    return Generation(prompt=prompt, content=result)

class UIGen(Domain):
    def __init__(self, data_dir: str, model: str = text_model, console: Console = Console()):
        super().__init__(
            name="ui", 
            display_name="UI", 
            data_dir=data_dir, 
            model=model, 
            console=console, 
            scripts_path="domains/ui/ui_scripts.js")

    def generate_one(self, concept: str, design_space: DesignSpace, model: str = text_model) -> Generation:
        return generate_ui(concept, design_space, text_model=model)
