import os
import argparse
from pathlib import Path
from rich.console import Console

from domains.dormroom.dormroom_viewer import DormRoomViewer

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SVG Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/dormroom/examples', 
                        help='Directory containing SVG files')
    parser.add_argument('--output-dir', type=str, default='../.data/dormroom/examples', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8002, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    viewer = DormRoomViewer(
        dormroom_folder=str(data_dir),
        output_path=str(output_dir),
        concept="examples",
        title="DormRoom Viewer",
        port=args.port,
        console=console
    )
    
    # Run the viewer
    feedback_data = viewer.run()
    
    # Print the feedback data
    console.print(feedback_data)

if __name__ == "__main__":
    main() 