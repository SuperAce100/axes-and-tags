import re
from typing import List
from pydantic import BaseModel
from models.llms import text_model, llm_call
from models.prompts import (
    fill_design_space_prompt,
    create_design_space_prompt,
    explore_axis_prompt,
)


class Axis(BaseModel):
    name: str
    status: str
    value: str


class DesignSpace(BaseModel):
    concept: str
    domain: str
    axes: List[Axis]

    def __str__(self):
        return "\n".join(
            [f"{axis.name} ({axis.status}) : {axis.value}" for axis in self.axes]
        )

    @staticmethod
    def create(concept: str, domain: str, model: str = text_model, context: str | None = None):
        prompt = create_design_space_prompt.format(concept=concept, domain=domain)
        if context:
            prompt += "\n\nHere is additional context to inform the design space:\n" + context

        response = llm_call(prompt, model=model)

        axes = []
        axes_parts = response.split("<axis>")
        if len(axes_parts) > 1:
            for axis in axes_parts[1:]:
                if "</axis>" in axis:
                    axis_name = axis.split("</axis>")[0].strip()
                    axes.append(Axis(name=axis_name, status="unconstrained", value=""))
                else:
                    continue

        return DesignSpace(concept=concept, domain=domain, axes=axes)

    def get_axis(self, name: str) -> Axis:
        for axis in self.axes:
            if axis.name == name:
                return axis
        return None

    def explore_new_axis(self) -> None:
        exploring_axes = [axis for axis in self.axes if axis.status == "exploring"]
        if not exploring_axes:
            for axis in self.axes:
                if axis.status == "unconstrained":
                    axis.status = "exploring"
                    return

    def explore(self, n: int, model: str = text_model) -> List[str]:
        exploring_axis = [axis for axis in self.axes if axis.status == "exploring"][0]
        for axis in self.axes:
            if axis != exploring_axis and axis.status == "exploring":
                axis.status = "unconstrained"
        if not exploring_axis:
            return []

        response = llm_call(
            explore_axis_prompt.format(
                concept=self.concept, domain=self.domain, axis=exploring_axis.name, n=n
            ),
            model=model,
        )

        print(response)

        options = []
        options_parts = response.split("<options")
        if len(options_parts) > 1:
            for option in options_parts[1:]:
                if "</options>" in option:
                    option_values = re.findall(r"<option>(.*?)</option>", option)
                    options.extend(option_values)

        return options

    def fill(self, model: str = text_model):
        """
        Fill in all unconstrained axes with a value.
        """
        unconstrained_axes = [
            axis
            for axis in self.axes
            if axis.status == "unconstrained" and axis.value == ""
        ]

        if not unconstrained_axes:
            return

        unconstrained_axes_str = "\n".join(
            [f"{axis.name}: {axis.value}" for axis in unconstrained_axes]
        )

        response = llm_call(
            fill_design_space_prompt.format(
                concept=self.concept, domain=self.domain, axes=unconstrained_axes_str
            ),
            model=model,
        )

        for axis_line in response.strip().split("\n"):
            if "<axis" in axis_line and "</axis>" in axis_line:
                name_match = re.search(r'name="([^"]+)"', axis_line)
                if name_match:
                    axis_name = name_match.group(1)
                    axis_value = (
                        axis_line.split(">", 1)[1].split("</axis>", 1)[0].strip()
                    )
                    self.get_axis(axis_name).value = axis_value


class Tag(BaseModel):
    dimension: str
    value: str


class Generation(BaseModel):
    prompt: str
    content: str


class Example(BaseModel):
    prompt: str
    content: str
    tags: List[Tag]
