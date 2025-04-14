examples_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""




svg_system_prompt = """
You will need to generate an SVG image of a concept in an flat, colored style. There should be no background color.

{examples}
"""

svg_user_prompt = """
Generate an SVG image of a {concept}
"""
