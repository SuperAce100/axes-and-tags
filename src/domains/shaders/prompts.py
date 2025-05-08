shader_system_prompt = """
You must generate a shader based on a given prompt.

The shader must be wrapped in a <shader></shader> XML tag, like this:

<shader>
<!-- SHADER HERE -->
</shader>

The shader must be a valid shader written in GLSL. The shader should be designed so it can be visualized in Shadertoy. This means it should be entirely contained within a function with the signature: 
    void mainImage(out vec4 fragColor, in vec2 fragCoord)

Make sure to follow every single instruction provided in the prompt carefully, and comment your code extensively.
"""

shader_expand_system_prompt = """
You are a helpful assistant that expands prompts for shader generation.

You will be given a concept and a list of examples.

You will need to expand the concept into a more simple prompt that contains an idea for a shader.

The expanded prompt should be more specific and detailed than the original concept, but not too complex. It should take into account things that are possible to render in a GLSL shader.

The expanded prompt should be in the style of the examples.

Here are some examples:

<examples>
{examples}
</examples>
"""

shader_expand_system_prompt_extend = """
You must generate {n} new prompts for the user, ALL of which must follow EVERY piece of feedback provided. Make them all meaningfully different by varying styles, objects, and adjectives while keeping specified deta

If you've recieved feedback on any previous generations, make sure to include that feedback in each new prompt - EVERY NEW PROMPT MUST INCOPORATE ALL THE FEEDBACK.

IMPORTANT: You must surround each new prompt with <prompt></prompt> XML tags, like this:

<prompt>
EXAMPLE PROMPT HERE
</prompt>
"""

shader_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>
"""

shader_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

shader_feedback_format = """
{example}

Here are the things the user likes about the shader:

{feedback}
"""
shader_insights_format = """
Here are some prompts used to generate shaders
{feedback}
In a future shader generation, which specific visual elements and effects need to be retained and which ones need to be changed. ONLY include a list of very specific shader features with detailed descriptions that must be constant in future generations. (not "colorful effects" but "a radial gradient from deep purple (#2a0845) at the center to vibrant pink (#6441A5) at the edges with smooth transitions")

Think about it as a list of shader techniques and visual qualities that must be consistent in future generations, based on the preferences expressed by the user. If they say they like the glowing particles in a shader that includes animated floating specks with bloom effects, it means that all future generations must include animated particle systems with bloom post-processing.

DO not adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked.

After defining the list of features that must be consistent, present a list of 3-5 features that can be varied.
"""

shader_tags_format = """
Here is a prompt:

<prompt>
{prompt}
</prompt>

Extract a set of 3-5 useful tags from the prompt. These could be objects, actions, adjectives, etc all present in the prompt. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which the propmt is constucted.

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