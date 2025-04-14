examples_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""

svg_system_prompt = """
You will need to generate an SVG image of a concept in an outline style. All elements should have a stroke of 2px solid black and no fill. Don't overlap elements.
{examples}
"""

svg_user_prompt = """
Generate an SVG image of a {concept}
"""
