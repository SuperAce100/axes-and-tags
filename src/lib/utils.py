import random
import re
import time

def parse_svg(response: str) -> str:
    # Extract SVG content between <svg> tags
    svg_match = re.search(r'<svg.*?</svg>', response, re.DOTALL)
    if svg_match:
        return svg_match.group(0)
    return response

def parse_threejs(response: str) -> str:
    # Extract JavaScript code between ```js or ```javascript blocks
    js_match = re.search(r'```(?:js|javascript)\n(.*?)\n```', response, re.DOTALL)
    if js_match:
        return js_match.group(1)
    return response

def parse_dsl(response: str) -> str:
    # Extract code between <response> tags
    dsl_match = re.search(r'<response>\n(.*?)\n</response>', response, re.DOTALL)
    if dsl_match:
        return dsl_match.group(1)
    return response


if __name__ == "__main__":
    example_response = """
    Here's a simple and cute SVG of a cartoon-style cat:

    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <!-- Body -->
    <ellipse cx="100" cy="140" rx="50" ry="40" fill="#DDB892" />

    <!-- Head -->
    <circle cx="100" cy="80" r="35" fill="#DDB892" />

    <!-- Ears -->
    <polygon points="75,50 85,20 95,50" fill="#DDB892" />
    <polygon points="105,50 115,20 125,50" fill="#DDB892" />

    <!-- Eyes -->
    <circle cx="90" cy="75" r="5" fill="#000" />
    <circle cx="110" cy="75" r="5" fill="#000" />

    <!-- Nose -->
    <circle cx="100" cy="85" r="3" fill="#333" />

    <!-- Mouth -->
    <path d="M95,92 Q100,97 105,92" stroke="#333" stroke-width="2" fill="none" />

    <!-- Whiskers -->
    <line x1="65" y1="85" x2="85" y2="85" stroke="#333" stroke-width="2" />
    <line x1="65" y1="90" x2="85" y2="88" stroke="#333" stroke-width="2" />
    <line x1="65" y1="80" x2="85" y2="82" stroke="#333" stroke-width="2" />

    <line x1="115" y1="85" x2="135" y2="85" stroke="#333" stroke-width="2" />
    <line x1="115" y1="88" x2="135" y2="90" stroke="#333" stroke-width="2" />
    <line x1="115" y1="82" x2="135" y2="80" stroke="#333" stroke-width="2" />
    </svg>

    You can copy and paste this into an .svg file or directly into an HTML file to render it. Want it in a specific style (realistic, minimalist, anime, etc.) or doing something funny like playing with yarn?
    """

    print(parse_svg(example_response))
