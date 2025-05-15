from ast import Tuple
from collections.abc import Callable
import os
from pathlib import Path
from rich.console import Console
import argparse
from viewer.viewer import Viewer
from typing import Dict, Tuple
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
                 concept: str = "image",
                 used_examples: list[str] = None,
                 design_space: dict[str, Tuple[str, str]] = None,
                 update_design_space: Callable[[Dict[str, Tuple[str, str]], Dict[str, list[str]]], None] = None):
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
            custom_scripts_path="domains/imagegen/image_scripts.js",
            used_examples=used_examples,
            design_space=design_space,
            update_design_space=update_design_space
        )
    
    
    
        


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Image Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/imagegen/results/dog_1746519682_9003/', 
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
    i = 0

    while "feedback" in os.listdir(data_dir):
        i += 1
        data_dir = os.path.join(data_dir, "feedback")
        viewer = ImageViewer(
            image_folder=str(data_dir),
            output_path=str(output_dir),
            concept="examples",
            title="Image Viewer",
            port=args.port + i,
            console=console,
            used_examples=feedback_data
        )
        new_feedback_data = viewer.run()
        # if not new_feedback_data:
        #     break

        console.print(new_feedback_data)

        feedback_data = {f"../{k}": v for k, v in feedback_data.items()}
        feedback_data = {**feedback_data, **new_feedback_data}


if __name__ == "__main__":
    main() 