import os
import argparse
from pathlib import Path
from rich.console import Console

from src.viewer.viewer import Viewer

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generic Viewer Example')
    parser.add_argument('--data-dir', type=str, default='.data/examples', 
                        help='Directory containing data files')
    parser.add_argument('--output-dir', type=str, default='.data/examples/selected', 
                        help='Directory to save selected files')
    parser.add_argument('--custom-scripts-dir', type=str, default='.data/examples/custom', 
                        help='Directory containing custom scripts')
    parser.add_argument('--port', type=int, default=8001, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    # Create directories if they don't exist
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    custom_scripts_dir = Path(args.custom_scripts_dir)
    custom_scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some example files
    example_files = [
        ("example1.txt", "This is example file 1"),
        ("example2.txt", "This is example file 2"),
        ("example3.txt", "This is example file 3"),
    ]
    
    for filename, content in example_files:
        file_path = data_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
    
    # Create a custom scripts.js file for this example
    custom_scripts_path = custom_scripts_dir / "scripts.js"
    with open(custom_scripts_path, "w") as f:
        f.write("""
// Custom scripts for the example viewer
console.log("Custom scripts loaded!");

// Override the renderFiles function to display files differently
function renderFiles() {
    const grid = document.getElementById('mainGrid');
    grid.innerHTML = '';
    
    files.forEach((file, index) => {
        const container = document.createElement('div');
        container.className = 'preview-container custom-style';
        container.id = `preview-${index}`;
        
        const header = document.createElement('div');
        header.className = 'preview-header';
        header.textContent = file.name;
        
        const content = document.createElement('div');
        content.className = 'preview-content';
        content.textContent = file.content;
        
        container.appendChild(header);
        container.appendChild(content);
        
        // Add click event to select the file
        container.addEventListener('click', () => {
            selectFile(file.name);
        });
        
        // Add double click event to save the file
        container.addEventListener('dblclick', () => {
            saveSelected();
        });
        
        // Highlight selected file
        if (file.name === selectedFile) {
            container.classList.add('selected');
            selectedIndex = index;
        }
        
        grid.appendChild(container);
    });
}

// Load files when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
});
""")
    
    # Initialize the viewer
    viewer = Viewer(
        data_folder=str(data_dir),
        output_path=str(output_dir),
        domain="example",
        title="Example Viewer",
        port=args.port,
        console=console,
        file_extension=".txt",
        custom_scripts_path=f"/custom/scripts.js"
    )
    
    # Run the viewer
    feedback_data = viewer.run()
    
    # Print the feedback data
    console.print(feedback_data)

if __name__ == "__main__":
    main() 