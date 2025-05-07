svg_system_prompt = """
You are a helpful assistant that generates SVG images of a concept.

You will be given a concept and a list of examples.

You will need to generate an SVG image of the concept.

The SVG should be in the style of the examples.

Comment your SVG extensively to explain the unique stylistic choices you made in each generation and label 

Here are some examples:

<examples>
{examples}
</examples>

You must generate {n} new and UNIQUE SVGs for the user, ALL of which must follow EVERY piece of feedback provided

If you've recieved feedback on any previous generations, make sure to include that feedback in each new SVG - EVERY NEW SVG MUST INCOPORATE ALL THE FEEDBACK.

If all you've recieved are examples, inspire your SVGs from the examples but don't follow them exactly. Make sure all {n} SVGs are unique and different from each other.

IMPORTANT: You must surround each new SVG with <result></result> XML tags, like this:

<result>
EXAMPLE SVG HERE
</result>
"""


svg_user_prompt = """
Generate an SVG image of a {concept}.
"""

svg_examples_format = """
Here is an example of a {concept}:

<example>
{example}
</example>
"""

svg_feedback_format = """
{example}

Here are the things the user likes about the SVG:

{feedback}
"""

svg_insights_format = """
Here are some SVGs used to generate images
{feedback}
In a future SVG generation, which specific features need to be retained and which ones need to be changed. ONLY include a list of very specific features with detailed descriptions that must be constant in the future generation. (not "the head, the tail" but "an egg shaped head, a tail with a curvy shape")

Think about it as a list of features and adjectives that must be consistent in the future generations, based on the preferences expressed by the user. If they say they like a flat color style, it means that all future generations must be in a flat color style.

DO not adlib anything the user did not specifically mention in their feedback. Extract only what the user explicitly said they liked.
"""

svg_tags_format = """
Here is an SVG:

<svg>
{svg}
</svg>

Extract a set of 3-5 useful tags from the SVG. These could be objects, features, adjectives, styles, etc all present in the SVG. 

Each tag should be atomic and 1-3 words, and extremely brief, specific, and descriptive. They should be the building blocks on top of which future SVGs can be built.

Every tag should represent an obvious stylistic choice for the SVG or an optional element present like "red color", "rounded", "flat style", "sitting pose", "green eyes", etc.

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