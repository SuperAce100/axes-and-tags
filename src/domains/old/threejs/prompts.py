threejs_system_prompt = """
You will need to generate Three.js code to create {n} 3D models of a concept. The code should:

1. For each generation, define a function named `createObject` that takes a container parameter:
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
   - Add all objects to the group
   - Return the group (not the scene)

   Do not include any imports or any other code outside of the function.
The code should be complete and runnable. Use modern Three.js practices and ensure the model is optimized.

Comment your code extensively to explain the unique stylistic choices you made in each generation and label 

Here are some examples with feedback:
<examples>
{examples}
</examples>

You must generate {n} new and UNIQUE models for the user, ALL of which must follow EVERY piece of feedback provided

If you've recieved feedback on any previous generations, make sure to include that feedback in each new model - EVERY NEW MODEL MUST INCOPORATE ALL THE FEEDBACK.

If all you've recieved are examples, inspire your models from the examples but don't follow them exactly. Make sure all {n} models are unique and different from each other.

IMPORTANT: You must surround each new model with <result></result> XML tags, like this:

<result>
EXAMPLE MODEL HERE
</result>
"""


threejs_user_prompt = """
Generate a 3D model of a {concept}.
"""

threejs_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

threejs_feedback_format = """
{example}

Here are the things the user likes about the model:

{feedback}
"""

threejs_insights_format = """
Here are some models used to generate images
{feedback}
In a future model generation, which specific features need to be retained and which ones need to be changed. ONLY include a list of very specific features with detailed descriptions that must be constant in the future generation. (not "the head, the tail" but "an egg shaped head, a tail with a curvy shape")

Think about it as a list of features and adjectives that must be consistent in the future generations, based on the preferences expressed by the user. If they say they like a flat color style, it means that all future generations must be in a flat color style.

DO not adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked.
"""

threejs_tags_format = """
Here is a model:

<model>
{model}
</model>

Extract a set of 3-5 useful tags from the model. These could be objects, features, adjectives, styles, etc all present in the model. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which future models can be built.

Every tag should represent an obvious stylistic choice for the model or an optional element present like "red color", "rounded", "flat style", "sitting pose", "green eyes", etc.

Enclose each tag in <tag></tag> XML tags, like this, and return the list of tags in a <tags></tags> XML tag:

<tags>
<tag>TAG HERE</tag>
<tag>TAG HERE</tag>
<tag>TAG HERE</tag>
</tags>

Here are some tags that have already been used:

<old_tags>
{old_tags}
</old_tags>

Every tag you generate MUST NOT be in the old_tags list.
"""