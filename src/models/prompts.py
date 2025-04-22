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

threejs_system_prompt = """
You will need to generate Three.js code to create a 3D model of a concept.

1. Define a function named `createObject` and include your code in there
   
Here are some examples
{examples}
"""

threejs_user_prompt = """
Generate Three.js code to create a 3D model of a {concept}.
"""

feedback_example_format = """
Here is a past example you made of a {concept}

<example>
{example}
</example>

A human has reviewed the example and given you some feedback:

<feedback>
{feedback}
</feedback>
"""

# dsl_description = """
