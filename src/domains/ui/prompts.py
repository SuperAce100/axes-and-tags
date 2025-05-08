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
ui_insights_format = """
Here are some prompts used to generate UIs
{feedback}
In a future prompt generation, which specific features need to be retained and which ones need to be changed. ONLY include a list of very specific features with detailed descriptions that must be constant in the future generation. (not "the button layout" but "a primary action button centered at the bottom with rounded corners and a blue gradient background")

Think about it as a list of features and adjectives that must be consistent in the future generations, based on the preferences expressed by the user. If they say they like the navigation in an interface that includes a side drawer menu, it means that all future generations must include a side drawer menu.

DO not adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked. Focus on UI elements, layouts, colors, interactions and visual hierarchy.

After defining the list of features that must be consistent, present a list of 3-5 features that can be varied.
"""

ui_tags_format = """
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