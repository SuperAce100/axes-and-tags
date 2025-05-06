import random

threejs_system_prompt = """
You will need to generate Three.js code to create a 3D model of a concept.

1. Define a function named `createObject` and include your code in there
   
Here are some examples
{examples}
"""

threejs_user_prompt = """
Generate Three.js code to create a 3D model of a {concept}.
"""
