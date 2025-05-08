# Generic Viewer

A flexible viewer component that can be used across different domains to visualize and interact with files.

## Features

- View and navigate through files in a grid layout
- Add feedback to files
- Save selected files
- Keyboard shortcuts for navigation and actions
- Customizable scripts for domain-specific rendering
- FastAPI backend for efficient file serving

## Usage

### Basic Usage

```python
from src.viewer.viewer import Viewer
from rich.console import Console

# Initialize the viewer
viewer = Viewer(
    data_folder="path/to/data",
    output_path="path/to/output",
    domain="your_domain",
    title="Your Viewer Title",
    port=8001,
    console=Console(),
    file_extension=".your_extension"
)

# Run the viewer
feedback_data = viewer.run()
```

### Advanced Usage with Custom Scripts

```python
from src.viewer.viewer import Viewer
from rich.console import Console

# Initialize the viewer with custom scripts
viewer = Viewer(
    data_folder="path/to/data",
    output_path="path/to/output",
    domain="your_domain",
    title="Your Viewer Title",
    port=8001,
    console=Console(),
    file_extension=".your_extension",
    custom_scripts_path="/path/to/custom/scripts.js"
)

# Run the viewer
feedback_data = viewer.run()
```

## Parameters

- `data_folder`: Path to the folder containing data files
- `output_path`: Path to save the selected object
- `domain`: Domain name for the output file
- `title`: Title for the viewer
- `port`: Port to run the server on
- `console`: Rich console for output
- `file_extension`: Extension of files to display (default: .dsl)
- `custom_scripts_path`: Path to custom scripts.js file

## Keyboard Shortcuts

- `←`: Previous file
- `→`: Next file
- `Enter`: Select / Save Feedback
- `Esc`: Close Viewer
- `S` or `Double Click`: Save Selected as Example

## Custom Scripts

You can provide a custom `scripts.js` file to override the default behavior of the viewer. This is useful for domain-specific rendering or additional functionality.

Example of a custom script:

```javascript
// Custom scripts for the viewer
console.log("Custom scripts loaded!");

// Override the renderFiles function to display files differently
function renderFiles() {
    // Your custom rendering logic here
}

// Load files when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});
```

## Examples

See the `examples` directory for usage examples:

### Generic Viewer Example

```bash
python -m src.viewer.examples.generic_viewer_example --data-dir /path/to/data --output-dir /path/to/output --port 8001
```

Command line arguments:
- `--data-dir`: Directory containing data files (default: .data/examples)
- `--output-dir`: Directory to save selected files (default: .data/examples/selected)
- `--custom-scripts-dir`: Directory containing custom scripts (default: .data/examples/custom)
- `--port`: Port to run the server on (default: 8001)

### DormRoom Viewer Example (Legacy)

```bash
python -m src.viewer.examples.dormroom_viewer_example --data-dir /path/to/data --output-dir /path/to/output --port 8001
```

Command line arguments:
- `--data-dir`: Directory containing data files (default: .data/dormroom/examples)
- `--output-dir`: Directory to save selected files (default: .data/dormroom/examples/selected)
- `--port`: Port to run the server on (default: 8001)

## Backward Compatibility

For backward compatibility, the `DormRoomViewer` class is still available:

```python
from src.viewer.viewer import DormRoomViewer

viewer = DormRoomViewer(
    js_folder="path/to/js",
    output_path="path/to/output",
    concept="your_concept",
    title="Your Viewer Title",
    port=8001
)

feedback_data = viewer.run()
``` 