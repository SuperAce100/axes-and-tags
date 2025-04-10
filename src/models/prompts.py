examples_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""

svg_system_prompt = """
You are an expert SVG designer. You will need to generate an SVG image of a concept in an outline style. All elements should have a stroke of 2px solid black and no fill.

Always return only the SVG code, nothing else, in a valid SVG format. Comment the SVG code extensively with your thought process.

{examples}
"""

svg_user_prompt = """
Generate an SVG image of a {concept}
"""
