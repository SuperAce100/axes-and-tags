import argparse
from pathlib import Path
from rich.console import Console
from typing import List
from viewer.viewer import Viewer

class SVGViewer(Viewer):
    """
    A specialized viewer for SVG files.
    """
    def __init__(self, 
                 svg_folder: str, 
                 output_path: str = None, 
                 concept: str = None, 
                 title: str = "SVG Viewer", 
                 port: int = 8002, 
                 console: Console = None,
                 used_examples: List[str] = None):
        """
        Initialize the SVGViewer.
        
        Args:
            svg_folder (str): Path to the folder containing SVG files
            output_path (str, optional): Path to save the selected object
            concept (str, optional): Concept name for the output file
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(svg_folder),
            output_path=output_path,
            concept=concept,
            title=title,
            port=port,
            console=console,
            custom_scripts_path="domains/svg/svg_scripts.js",
            used_examples=used_examples
        )
        


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SVG Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/flat/examples', 
                        help='Directory containing SVG files')
    parser.add_argument('--output-dir', type=str, default='../.data/flat/examples', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8002, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    viewer = SVGViewer(
        svg_folder=str(data_dir),
        output_path=str(output_dir),
        concept="examples",
        title="SVG Viewer",
        port=args.port,
        console=console
    )
    
    # Run the viewer
    feedback_data = viewer.run()
    
    # Print the feedback data
    console.print(feedback_data)

if __name__ == "__main__":
    main() 