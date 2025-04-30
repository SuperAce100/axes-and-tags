

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
Here is an example of a {concept}:

<example>
{example}
</example>

A human has given feedback on the example:

<feedback>
{feedback}
</feedback>
"""