

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
You must generate {n} new prompts for the user, each following the feedback and examples provided.

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

Here is some feedback on the image generated from this prompt:

{feedback}
"""


image_gen_insights_format = """
Here are some prompts used to generate images
{feedback}
In a future prompt generation, which specific features need to be retained and which ones need to be changed. ONLY include a list of very specific features that must be constant in the future generation. (not "the elephant, the background" but "an african elephant with large ears, background: a clear night sky next to a lake")

Think about it as a list of features that must be consistent in the future generations, based on the preferences expressed by the user. If they say they like the cats in an image that includes a black cat, it means that all future generations must include a black cat.
"""
