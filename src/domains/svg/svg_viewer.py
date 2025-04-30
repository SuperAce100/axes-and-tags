import os
import shutil
from pathlib import Path
from rich.console import Console

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
                 console: Console = None):
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
            file_extension=".svg",
            custom_scripts_path="domains/svg/svg_scripts.js"
        )
        
