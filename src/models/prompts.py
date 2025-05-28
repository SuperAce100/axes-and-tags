create_design_space_prompt = """
You are tasked with creating a design space for a {domain} of a {concept}.

Generate a list of axes of the design space that is relevant to the concept and domain. For example, for an image of a car, the design space could be "car_type", "car_color", "background", "camera_angle", etc... There should be between 4-6 concrete axes. Each axis should be 1-4 words and not duplicate the others.

Return the list of axes in a <axes></axes> XML tag, like this:

<axes>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
<axis>AXIS HERE</axis>
</axes>
"""

extract_tags_prompt = """
Here is a prompt:

<prompt>
{prompt}
</prompt>

And here is a design space:
{design_space}

Extract exactly one tag for each axis in the design space that's labeled "exploring" or "unconstrained", describing the value of the axis in a concise manner (1-4 words)

Enclose each tag in <tag></tag> XML tags, like this, and return the list of tags in a <tags></tags> XML tag:

<tags>
<tag dimension="dimension_name">TAG HERE</tag>
<tag dimension="dimension_name">TAG HERE</tag>
<tag dimension="dimension_name">TAG HERE</tag>
</tags>
"""

fill_design_space_prompt = """
Here is set of axes in the design space for a {domain} of a {concept}:

<axes>
{axes}
</axes>

Come up with the most likely value for each axis.

Return the design space in a <axes></axes> XML tag, like this:

<axes>
<axis name="AXIS NAME HERE">AXIS VALUE HERE</axis>
<axis name="AXIS NAME HERE">AXIS VALUE HERE</axis>
<axis name="AXIS NAME HERE">AXIS VALUE HERE</axis>
</axes>
"""

explore_axis_prompt = """
Here is an axis in the design space of a {domain} of a {concept}:
{axis}

Create {n} possible values for the axis. They should be meaningfully different and vary along only this axis. If the axis is continuous in any way, organize your options along that (like shortest to tallest, darkest to lightest, etc...)

Return the axis in a <options></options> XML tag, like this:

<options>
<option>OPTION HERE</option>
<option>OPTION HERE</option>
<option>OPTION HERE</option>
</options>
"""
