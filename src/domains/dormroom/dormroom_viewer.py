from pathlib import Path
from rich.console import Console
import argparse
from viewer.viewer import Viewer

class DormRoomViewer(Viewer):
    """
    A specialized viewer for SVG files.
    """
    def __init__(self, 
                 dormroom_folder: str, 
                 output_path: str = None, 
                 title: str = "DormRoom Viewer", 
                 port: int = 8002, 
                 console: Console = None):
        """
        Initialize the DormRoomViewer.
        
        Args:
            dormroom_folder (str): Path to the folder containing DormRoom files
            output_path (str, optional): Path to save the selected object
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(dormroom_folder),
            output_path=output_path,
            concept="dormroom",
            title=title,
            port=port,
            console=console,
            file_extension=".dsl",
            custom_scripts_path="domains/dormroom/dormroom_scripts.js"
        )
        


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