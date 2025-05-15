
text_gen_multiple_system_prompt = """
You are a helpful assistant that generates text content.

You will need to write {n} different pieces of text for the user that all follow the same concept.

The expanded text should be in the style of the examples.

Here are some constraints

<constraints>
{examples}
</constraints>

You must generate {n} new pieces of text for the user, ALL of which must follow EVERY piece of feedback provided. Make them all meaningfully different by varying tone, word choice, structure, and style while keeping specified details.

Explicitly vary the different generations across the axes provided. For example, one email could propose a time to meet, and another could wait for the recipient to respond.

You might be given a specific list of features that are constrained in the new text. Keep these exactly the same across all new texts. You might also be given a list of features that are to be explored. Each of your generations should significantly vary these features.

IMPORTANT: You must surround each new text with <text></text> XML tags, like this:

<text>
EXAMPLE TEXT HERE
</text>
"""

text_gen_multiple_user_prompt = """
Here is the concept you need to write about:

<concept>
{concept}
</concept>
"""

text_gen_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

text_gen_feedback_format = """
Here are the things the user likes about the text:

{feedback}
"""

text_gen_temp_design_space_format = """
Here is a design space:
{design_space}

Based on the values in the design space, and the feedback from the user, fill in any axes specificaly labeled unconstrained in the design space with an arbitrarily chosen value.

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name" status="constrained|unconstrained|exploring">axis_value</axis>. For example:

<design_space>
<axis name="formality" status="constrained">conversational with slang</axis>
<axis name="tone" status="constrained">lighthearted and humorous</axis>
<axis name="topic" status="exploring">backpacking through Southeast Asia</axis>
<axis name="length" status="unconstrained">150-200 words</axis>
</design_space>
"""

text_gen_tags_format = """
Here is a text:

<text>
{text}
</text>

And here is a design space:
{design_space}

Extract a set of useful tags from the text. These could be objects, actions, adjectives, etc all present in the text. 

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

text_gen_get_design_space_prompt = """
Here is a concept that you will be generating text about: {concept}

Generate a list of axes of the design space that is relevant to the concept and can enable a wide variety of different outputs. They should explicitly define axes where diversity can be achieved. 

For example, for a concept of "recipe", the design space could be "cuisine type", "dietary restrictions", "cooking skill level", "prep time", "serving size", "meal type". Or for "product review", it could be "technical depth", "comparison focus", "target audience", "writing style", "product category", "review length".

You could also propose something like "proposing time?" where what is varied is whether the user proposes a time to meet or waits for the recipient to respond.

There should be between 4-6 concrete axes. Each axis should be 1-4 words and not duplicate the others.

Return the list of axes in a <axes></axes> XML tag, like this:

<axes>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
</axes>
"""

text_gen_update_design_space_prompt = """
You are tasked with updating a design spaced based on a summary of what the user likes and dislikes.

Here is the design space:
{design_space}

Here is the feedback from the user:
{feedback_data}

Update the design space based on the feedback, only updating axes that are not fixed based on the feedback itself, and only updating the value of the axis if the user has explicitly mentioned it in their feedback. YOU MUST leave axes blank if the user has not mentioned it in their feedback. Update every axis that you take from the feedback. When you update an axis, make sure to set the status to "constrained".

Of the axes that are not constrained, choose another axis to explore, and leave the rest of the axes unconstrained. If one is already exploring, don't change it.

Return the updated design space in a <design_space></design_space> XML tag, with each axis represented as a key-value pair in the format <axis name="axis_name" status="constrained|unconstrained|exploring">axis_value</axis>. For example:

<design_space>
<axis name="formality" status="constrained">conversational with slang</axis>
<axis name="tone" status="constrained">lighthearted and humorous</axis>
<axis name="topic" status="exploring">backpacking through Southeast Asia</axis>
<axis name="length" status="unconstrained">150-200 words</axis>
</design_space>
"""