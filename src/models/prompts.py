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
You will need to generate Three.js code to create a 3D model of a concept. The code should:

1. Define a function named `createObject` that takes a container parameter:
   ```javascript
   function createObject(container) 
     // Create a group to hold all objects
     const group = new THREE.Group();
     
     // Create your 3D model here using THREE.js primitives
     // Add all objects to the group
     
     // Return the group
     return group;
   
   ```
2. Inside the function:
   - Create a group to hold all objects
   - Create the 3D model using Three.js geometry primitives
   - Add materials and textures
   - Add all objects to the group
   - Return the group (not the scene)

   Do not include any imports or any other code outside of the function.
The code should be complete and runnable. Use modern Three.js practices and ensure the model is optimized.

{examples}
"""

threejs_user_prompt = """
Generate Three.js code to create a 3D model of a {concept}. The code must:
1. Use regular script imports (THREE and OrbitControls from window)
2. Define a function named `createObject` that takes a container parameter
3. Create and return a THREE.Group containing all objects
4. Use proper materials and textures
5. Scale objects appropriately (around 1-2 units in size)
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
