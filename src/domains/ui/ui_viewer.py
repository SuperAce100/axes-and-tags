from pathlib import Path
from rich.console import Console
import argparse
from viewer.viewer import Viewer
from typing import List
class UIViewer(Viewer):
    """
    A specialized viewer for SVG files.
    """
    def __init__(self, 
                 ui_folder: str, 
                 output_path: str = None, 
                 title: str = "UI Viewer", 
                 port: int = 8002, 
                 console: Console = None,
                 concept: str = "ui",
                 used_examples: List[str] = None):
        """
        Initialize the UIViewer.
        
        Args:
            ui_folder (str): Path to the folder containing ui files
            output_path (str, optional): Path to save the selected object
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(ui_folder),
            output_path=output_path,
            concept=concept,
            title=title,
            port=port,
            console=console,
            custom_scripts_path="domains/ui/ui_scripts.js",
            used_examples=used_examples
        )
    
    
    
        


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='UI Viewer Example')
    parser.add_argument('--data-dir', type=str, default='../.data/ui/results/elephant', 
                        help='Directory containing ui files')
    parser.add_argument('--output-dir', type=str, default='../.data/ui/examples', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8002, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    
    viewer = UIViewer(
        ui_folder=str(data_dir),
        output_path=str(output_dir),
        concept="examples",
        title="UI Viewer",
        port=args.port,
        console=console
    )

    feedback_data = viewer.run()
    
    console.print(feedback_data)

if __name__ == "__main__":
    main() 