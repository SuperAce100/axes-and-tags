from pathlib import Path
from rich.console import Console
import argparse
from viewer.viewer import Viewer
from typing import List
class P5JSViewer(Viewer):
    """
    A specialized viewer for P5JS files.
    """
    def __init__(self, 
                 p5js_folder: str, 
                 output_path: str = None, 
                 title: str = "P5JS Viewer", 
                 port: int = 8002, 
                 console: Console = None,
                 concept: str = "p5js",
                 used_examples: List[str] = None):
        """
        Initialize the P5JSViewer.
        
        Args:
            p5js_folder (str): Path to the folder containing p5js files
            output_path (str, optional): Path to save the selected object
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(p5js_folder),
            output_path=output_path,
            concept=concept,
            title=title,
            port=port,
            console=console,
            custom_scripts_path="domains/p5js/p5_scripts.js",
            used_examples=used_examples
        )
    
    
    
        


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='P5JS Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/p5js/results/elephant', 
                        help='Directory containing p5js files')
    parser.add_argument('--output-dir', type=str, default='../.data/p5js/examples', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8002, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    viewer = P5JSViewer(
        p5js_folder=str(data_dir),
        output_path=str(output_dir),
        concept="examples",
        title="P5JS Viewer",
        port=args.port,
        console=console
    )

    feedback_data = viewer.run()
    
    console.print(feedback_data)

if __name__ == "__main__":
    main() 