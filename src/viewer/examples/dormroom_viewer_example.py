import os
import argparse
from pathlib import Path
from rich.console import Console

from src.viewer.viewer import DormRoomViewer

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DormRoom Viewer Example')
    parser.add_argument('--data-dir', type=str, default='.data/dormroom/examples', 
                        help='Directory containing data files')
    parser.add_argument('--output-dir', type=str, default='.data/dormroom/examples/selected', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8001, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    # Create directories if they don't exist
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some example DSL files
    example_files = [
        ("dorm1.dsl", "This is dorm room 1"),
        ("dorm2.dsl", "This is dorm room 2"),
        ("dorm3.dsl", "This is dorm room 3"),
    ]
    
    for filename, content in example_files:
        file_path = data_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
    
    # Initialize the viewer
    viewer = DormRoomViewer(
        js_folder=str(data_dir),
        output_path=str(output_dir),
        concept="dorm",
        title="Dorm Room Viewer",
        port=args.port,
        console=console
    )
    
    # Run the viewer
    feedback_data = viewer.run()
    
    # Print the feedback data
    console.print(feedback_data)

if __name__ == "__main__":
    main() 