from ast import Dict
from datetime import time
import os
from pathlib import Path
from typing import Any
from fastapi import HTTPException
from rich.console import Console
import argparse
from viewer.viewer import Viewer
import base64
import json

class ImageViewer(Viewer):
    """
    A specialized viewer for SVG files.
    """
    def __init__(self, 
                 image_folder: str, 
                 output_path: str = None, 
                 title: str = "Image Viewer", 
                 port: int = 8002, 
                 console: Console = None,
                 concept: str = "image"):
        """
        Initialize the ImageViewer.
        
        Args:
            image_folder (str): Path to the folder containing image files
            output_path (str, optional): Path to save the selected object
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(image_folder),
            output_path=output_path,
            concept=concept,
            title=title,
            port=port,
            console=console,
            file_extension=".json",
            custom_scripts_path="domains/imagegen/image_scripts.js"
        )
    
    async def get_files(self):
        """Get a list of all files in the folder with their content."""
        files = []
        for file in sorted(os.listdir(self.data_folder)):
            if file.lower().endswith(self.file_extension):
                file_path = self.data_folder / file
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                    files.append({
                        'name': file,
                        'content': content
                    })
                except Exception as e:
                    self.console.print(f"[bold red]Error reading {file}: {e}[/bold red]")
        self.console.print(f"[grey11]Rendering [bold cyan]{len(files)}[/bold cyan] files[/grey11]")
        return files
        


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Image Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/imagegen/results/elephant', 
                        help='Directory containing image files')
    parser.add_argument('--output-dir', type=str, default='../.data/imagegen/examples', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8002, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    viewer = ImageViewer(
        image_folder=str(data_dir),
        output_path=str(output_dir),
        concept="examples",
        title="Image Viewer",
        port=args.port,
        console=console
    )

    feedback_data = viewer.run()
    
    console.print(feedback_data)

if __name__ == "__main__":
    main() 