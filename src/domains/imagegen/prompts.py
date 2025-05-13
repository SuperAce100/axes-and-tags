

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

If you've recieved feedback on any previous generations, make sure to include that feedback in each new prompt - EVERY NEW PROMPT MUST INCOPORATE ALL THE FEEDBACK.

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

Here are the axes of the design space along which to explore. Do not explore axes that are fixed, only explore axes that do not have a value. If an axes has a value, it is fixed and you must include it in the list of features that must be consistent.
{design_space}

Think about it as a list of features and adjectives that must be consistent in the future generations, based on the preferences expressed by the user. If they say they like the cats in an image that includes a black cat, it means that all future generations must include a black cat. 

DO not adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked.

After defining the list of features that must be consistent, present a list of 3-5 features that can be varied.
"""

image_gen_tags_format = """
Here is a prompt:

<prompt>
{prompt}
</prompt>

And here is a design space:
{design_space}

Extract a set of 5-7 useful tags from the prompt. These could be objects, actions, adjectives, etc all present in the prompt. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which the prompt is constucted. The tags should be based on any empty axes in the design space.

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

Generate a list of axes of the design space that is relevant to the concept. For example, for a concept of "car", the design space could be "car_type", "car_color", "background", "camera_angle", etc... There should be between 5-10 axes. Each axis should be 1-4 words and not duplicate the others.

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

Update the design space based on the feedback, only updating axes that are not fixed based on the feedback itself, and only updating the value of the axis if the user has explicitly mentioned it in their feedback. YOU MUST leave axes blank if the user has not mentioned it in their feedback.

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name">axis_value</axis>. For example:

<design_space>
<axis name="car_type">sports</axis>
<axis name="car_color">red</axis>
<axis name="background">city street</axis>
</design_space>
"""