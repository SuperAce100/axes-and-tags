

image_gen_expand_system_prompt = """
You are a helpful assistant that expands prompts for image generation.

You will be given a concept and a list of examples.

You will need to expand the concept into a more detailed prompt that will be used to generate an image.

The expanded prompt should be more specific and detailed than the original concept.

The expanded prompt should be in the style of the examples.

Here are some examples:

<examples>
{examples}
</examples>
"""

image_gen_expand_system_prompt_extend = """
You must generate {n} new prompts for the user, ALL of which must follow EVERY piece of feedback provided. Make them all meaningfully different by varying styles, objects, camera angles, and adjectives while keeping specified details.

You might be given a specific list of features that are constrained in the new prompts. Keep these exactly the same across all new prompts. You might also be given a list of features that are to be explored. Each of your generations should significantly vary these features.

IMPORTANT: You must surround each new prompt with <prompt></prompt> XML tags, like this:

<prompt>
EXAMPLE PROMPT HERE
</prompt>
"""

image_gen_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>
"""

image_gen_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

image_gen_feedback_format = """
{example}

Here are the things the user likes about the image:

{feedback}
"""

image_gen_insights_format = """
Here are some prompts used to generate images
{feedback}
In a future prompt generation, which specific features need to be retained and which ones need to be changed. ONLY include a list of very specific features with detailed descriptions that must be constant in the future generation. (not "the elephant, the background" but "an african elephant with large ears, background: a clear night sky next to a lake")

Here are the axes of the design space along which to explore. Do not explore axes that are fixed, only explore axes that do not have a value and are labeled "exploring". If an axes has a value, it is fixed and you must include it in the list of features that must be consistent.
{design_space}

DO NOT adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked.

After defining the list of features that must be consistent, present a list of 3-5 features that can be varied.
"""

image_gen_temp_design_space_format = """
Here is a design space:
{design_space}

Based on the values in the design space, and the feedback from the user, fill in any axes specificaly labeled unconstrained in the design space with an arbitrarily chosen value.

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name" status="constrained|unconstrained|exploring">axis_value</axis>. For example:

<design_space>
<axis name="car_type" status="constrained">sports</axis>
<axis name="car_color" status="constrained">red</axis>
<axis name="background" status="exploring"></axis>
<axis name="camera_angle" status="unconstrained">wide angle</axis>
</design_space>
"""

image_gen_tags_format = """
Here is a prompt:

<prompt>
{prompt}
</prompt>

And here is a design space:
{design_space}

Extract a set of useful tags from the prompt. These could be objects, actions, adjectives, etc all present in the prompt. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which the prompt is constucted. The tags should be based on any empty axes in the design space.

The tags should be based on the design space, and there should be exactly ONE (1) tag for every axis labeled "exploring" or "unconstrained" in the design space.

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

image_gen_get_design_space_prompt = """
Here is a concept that you will be generating an image of: {concept}

Generate a list of axes of the design space that is relevant to the concept. For example, for a concept of "car", the design space could be "car_type", "car_color", "background", "camera_angle", etc... There should be between 4-6 concrete axes. Each axis should be 1-4 words and not duplicate the others.

Return the list of axes in a <axes></axes> XML tag, like this:

<axes>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
</axes>
"""

image_gen_update_design_space_prompt = """
You are tasked with updating a design spaced based on a summary of what the user likes and dislikes.

Here is the design space:
{design_space}

Here is the feedback from the user:
{feedback_data}

Update the design space based on the feedback, only updating axes that are not fixed based on the feedback itself, and only updating the value of the axis if the user has explicitly mentioned it in their feedback. YOU MUST leave axes blank if the user has not mentioned it in their feedback. Update every axis that you take from the feedback. When you update an axis, make sure to set the status to "constrained".

Of the axes that are not constrained, choose two axes to explore, and leave the rest of the axes unconstrained. 

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name" status="constrained|unconstrained|exploring">axis_value</axis>. For example:

<design_space>
<axis name="car_type" status="constrained">sports</axis>
<axis name="car_color" status="constrained">red</axis>
<axis name="background" status="exploring"></axis>
<axis name="camera_angle" status="unconstrained"></axis>
</design_space>
"""