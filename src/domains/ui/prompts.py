ui_system_prompt = """
You must generate a UI element based on a given prompt.

The UI must be wrapped in a <ui></ui> XML tag, like this:

<ui>
<!-- UI HERE -->
</ui>

The UI must be a valid HTML div element, and you should use Tailwind CSS classes to style it.

The outer level of the UI must be a div element, with the w-full and h-full classes, so it takes the full width and height of the container.

Make sure to follow every single instruction provided in the prompt carefully, and comment your code extensively.
"""

ui_expand_system_prompt = """
You are a helpful assistant that expands prompts for UI generation.

You will be given a concept and a list of examples.

You will need to expand the concept into a more detailed prompt that will be used to generate a UI element.

The expanded prompt should be more specific and detailed than the original concept.

The expanded prompt should be in the style of the examples.

Here are some examples:

<examples>
{examples}
</examples>
"""

ui_expand_system_prompt_extend = """
You must generate {n} new prompts for the user, ALL of which must follow EVERY piece of feedback provided. Make them all meaningfully different by varying styles, objects, and adjectives while keeping specified deta

If you've recieved feedback on any previous generations, make sure to include that feedback in each new prompt - EVERY NEW PROMPT MUST INCOPORATE ALL THE FEEDBACK.

IMPORTANT: You must surround each new prompt with <prompt></prompt> XML tags, like this:

<prompt>
EXAMPLE PROMPT HERE
</prompt>
"""

ui_expand_user_prompt = """
Expand the following concept:

<concept>
{concept}
</concept>
"""

ui_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

ui_feedback_format = """
{example}

Here are the things the user likes about the UI:

{feedback}
"""


ui_temp_design_space_format = """
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

ui_tags_format = """
Here is a prompt:

<prompt>
{prompt}
</prompt>

And here is a design space:
{design_space}

Extract a set of useful tags from the prompt. These could be objects, actions, adjectives, etc all present in the prompt. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which the prompt is constucted. The tags should be based on any empty axes in the design space.

The tags should be based on the design space, and there should be exactly ONE (1) tag for every axis labeled "exploring" or "unconstrained" in the design space. Do not create tags that are not based on the design space.

Enclose each tag in <tag></tag> XML tags, like this, and return the list of tags in a <tags></tags> XML tag:

<tags>
<tag dimension="dimension_name">TAG HERE</tag>
<tag dimension="dimension_name">TAG HERE</tag>
<tag dimension="dimension_name">TAG HERE</tag>
</tags>

Here are some tags that have already been used:

<old_tags>
{old_tags}
</old_tags>

Every tag you generate MUST NOT be in the old_tags list.
"""

ui_get_design_space_prompt = """
Here is a concept that you will be generating an image of: {concept}

Generate a list of axes of the design space that is relevant to the concept. For example, for a concept of "car", the design space could be "car_type", "car_color", "background", "camera_angle", etc... There should be between 4-6 concrete axes. Each axis should be 1-4 words and not duplicate the others.

Return the list of axes in a <axes></axes> XML tag, like this:

<axes>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
</axes>
"""

ui_update_design_space_prompt = """
You are tasked with updating a design spaced based on a summary of what the user likes and dislikes.

Here is the design space:
{design_space}

Here is the feedback from the user:
{feedback_data}

Update the design space based on the feedback, only updating axes that are not fixed based on the feedback itself, and only updating the value of the axis if the user has explicitly mentioned it in their feedback. YOU MUST leave axes blank if the user has not mentioned it in their feedback. Update every axis that you take from the feedback. When you update an axis, make sure to set the status to "constrained".

Of the axes that are not constrained, choose another axis to explore, and leave the rest of the axes unconstrained. If one is already exploring, don't change it.

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name" status="constrained|unconstrained|exploring">axis_value</axis>. For example:

<design_space>
<axis name="car_type" status="constrained">sports</axis>
<axis name="car_color" status="constrained">red</axis>
<axis name="background" status="exploring"></axis>
<axis name="camera_angle" status="unconstrained"></axis>
</design_space>
"""