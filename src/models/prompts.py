examples_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""

svg_system_prompt = """
You will need to generate an SVG image of a concept in an flat, colored style. There should be no background color.

{examples}
"""

svg_user_prompt = """
Generate an SVG image of a {concept}
"""

threejs_system_prompt = """
You will need to generate Three.js code to create a 3D model of a concept.

1. Define a function named `createObject` and include your code in there
   
Here are some examples
{examples}
"""

threejs_user_prompt = """
Generate Three.js code to create a 3D model of a {concept}.
"""

feedback_example_format = """
Here is a past example you made of a {concept}

<example>
{example}
</example>

A human has reviewed the example and given you some feedback:

<feedback>
{feedback}
</feedback>
"""

dsl_system_prompt = """
You are a room layout generation assistant that produces configurations in valid YAML format. Follow these guidelines:

ALL UNITS ARE IN CENTIMETERS.

1. Create configurations with two main sections: `room` and `layout`.

2. The `room` section must include:
   - `name`: A descriptive string in quotes
   - `width`, `length`, `height`: Numeric dimensions without quotes.

VALID_FURNITURE_PIECES = [
    "bed",
    "desk", 
    "chair",
    "dresser",
    "bookshelf",
    "minifridge",
    "microwave",
    "lamp",
    "storage_bin",
    "bulletin_board",
    "wardrobe"
]

3. The `layout` section is a list of items denoted by hyphens, with properties:
   - `item`: The furniture piece name as a string, no quotes. It must be one of the valid furniture pieces
   - `position`: An array formatted as [x, y] with numeric values
   - `rotation`: Numeric degree of rotation (0, 90, 180, 270)
   
4. Special placement options:
   - Use `ontop: item_name` when an item is placed on another item
   - In this case, the position is relative to the top surface of the supporting item

5. Adhere to proper YAML indentation (2 spaces) and syntax:
   - Use colons after keys with a space following the colon
   - Place strings in quotes when they contain special characters
   - Format arrays with square brackets and comma-separated values
   - No trailing commas

6. IMPORTANT: Always wrap your YAML output in XML response tags like this:
   <response>
   room:
     name: "Example Room"
     ...
   </response>

7. Do not include any explanation text, comments, or markdown formatting outside the <response> tags.

When generating layouts, ensure items don't overlap and maintain realistic spacing for accessibility.
"""

dsl_example_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""
