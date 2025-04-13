examples_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""

#  Don't include any suggestions, completely finish the SVG.

# Always return only the SVG code, nothing else, in a valid SVG format. Comment the SVG code extensively with your thought process.

# Here are some examples. Use them as inspiration and to understand how to effectively draw SVGs, but don't copy the exact design.

svg_system_prompt = """
You will need to generate an SVG image of a concept in an outline style. All elements should have a stroke of 2px solid black and no fill. Don't overlap elements.
{examples}
"""

svg_user_prompt = """
Generate an SVG image of a {concept}
"""
