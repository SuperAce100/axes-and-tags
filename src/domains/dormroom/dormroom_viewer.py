import os
import shutil
from pathlib import Path
from rich.console import Console

from src.viewer.viewer import Viewer

class DormRoomViewer:
    """
    A specialized viewer for dorm room DSL files using the generic Viewer class.
    """
    def __init__(self, 
                 js_folder: str, 
                 output_path: str = None, 
                 concept: str = None, 
                 title: str = "Dorm Room Viewer", 
                 port: int = 8001, 
                 console: Console = None):
        """
        Initialize the DormRoomViewer.
        
        Args:
            js_folder (str): Path to the folder containing DSL files
            output_path (str, optional): Path to save the selected object
            concept (str, optional): Concept name for the output file
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        self.js_folder = Path(js_folder)
        self.output_path = output_path
        self.concept = concept or "dorm"
        self.title = title
        self.port = port
        self.console = console or Console()
        
        # Create a custom scripts directory
        self.custom_scripts_dir = self.js_folder / "custom"
        self.custom_scripts_dir.mkdir(exist_ok=True)
        
        # Copy the dormroom scripts to the custom directory
        self.custom_scripts_path = self.custom_scripts_dir / "scripts.js"
        self._copy_dormroom_scripts()
        
        # Initialize the generic viewer
        self.viewer = Viewer(
            data_folder=str(self.js_folder),
            output_path=str(self.output_path) if self.output_path else None,
            domain=self.concept,
            title=self.title,
            port=self.port,
            console=self.console,
            file_extension=".dsl",
            custom_scripts_path=f"/custom/scripts.js"
        )
    
    def _copy_dormroom_scripts(self):
        """Copy the dormroom scripts to the custom directory."""
        # Get the path to the dormroom scripts
        dormroom_scripts_path = Path(__file__).parent / "dormroom_scripts.js"
        
        # Copy the scripts to the custom directory
        shutil.copy2(dormroom_scripts_path, self.custom_scripts_path)
        
        self.console.print(f"[grey11]Copied dormroom scripts to [bold cyan]{self.custom_scripts_path}[/bold cyan][/grey11]")
    
    def run(self, open_browser=True):
        """
        Run the viewer and return the feedback data.
        
        Args:
            open_browser (bool, optional): Whether to open the browser automatically
            
        Returns:
            dict: The feedback data
        """
        return self.viewer.run(open_browser=open_browser) 