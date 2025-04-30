import os
import shutil
from pathlib import Path
from rich.console import Console

from viewer.viewer import Viewer

class DormRoomViewer(Viewer):
    """
    A specialized viewer for SVG files.
    """
    def __init__(self, 
                 dormroom_folder: str, 
                 output_path: str = None, 
                 concept: str = None, 
                 title: str = "DormRoom Viewer", 
                 port: int = 8002, 
                 console: Console = None):
        """
        Initialize the DormRoomViewer.
        
        Args:
            dormroom_folder (str): Path to the folder containing DormRoom files
            output_path (str, optional): Path to save the selected object
            concept (str, optional): Concept name for the output file
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
        """
        
        super().__init__(
            data_folder=str(dormroom_folder),
            output_path=output_path,
            domain=concept or "dormroom",
            title=title,
            port=port,
            console=console,
            file_extension=".dsl",
            custom_scripts_path="domains/dormroom/dormroom_scripts.js"
        )
        
