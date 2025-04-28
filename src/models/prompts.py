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

1. Create configurations with one sections: `layout`.

VALID_FURNITURE_PIECES:
    "bed": width=90, length=200
    "desk": width=120, length=60
    "chair": width=40, length=40
    "dresser": width=60, length=40
    "bookshelf": width=80, length=30
    "minifridge": width=50, length=50
    "microwave": width=40, length=30
    "lamp": width=30, length=30
    "storage_bin": width=60, length=40
    "bulletin_board": width=80, length=2

3. The `layout` section is a list of items denoted by hyphens, with properties:
   - `item`: The furniture piece name as a string, no quotes. It must be one of the valid furniture pieces
   - `position`: An array formatted as [x, y] with numeric values. You are placing the center of the item at this position, so take into account the width and length of the item.
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
   layout:
     ...
   </response>

7. Do not include any explanation text, comments, or markdown formatting outside the <response> tags.

When generating layouts, ensure items don't overlap and maintain realistic spacing. For example, a bulletin board should be placed precisely on the wall, not on top of a desk.

The room has dimensions as follows. Do not repeat these in your response: {room_dimensions}

Here are some examples:
{examples}
"""

dsl_example_format = """
Here is an example of a {concept}

<example>
{example}
</example>
"""

example_room = """
room:
  name: "Dorm Room"
  width: 300
  length: 400
  height: 250
"""

dsl_user_prompt = """
Generate a layout for a {concept}.
"""