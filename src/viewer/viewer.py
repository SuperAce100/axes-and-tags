import os
import json
import random
import webbrowser
from pathlib import Path
import threading
import time
import shutil
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

class Viewer:
    def __init__(self, 
                 data_folder: str, 
                 output_path: Optional[str] = None, 
                 concept: Optional[str] = None, 
                 title: str = "3D Object Viewer", 
                 port: int = 8001, 
                 console: Optional[Console] = None,
                 file_extension: str = ".dsl",
                 custom_scripts_path: str = None,
                 used_examples: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the generic viewer.
        
        Args:
            data_folder (str): Path to the folder containing data files
            output_path (str, optional): Path to save the selected object
            domain (str, optional): Domain name for the output file
            title (str, optional): Title for the viewer
            port (int, optional): Port to run the server on
            console (Console, optional): Rich console for output
            file_extension (str, optional): Extension of files to display (default: .dsl)
            custom_scripts_path (str, optional): Path to custom scripts.js file
        """
        self.data_folder = Path(data_folder)
        self.output_path = output_path
        self.port = port
        self.selected_file = None
        self.feedback_data = {}
        self.server_running = False
        self.server_thread = None
        self.concept = concept
        self.title = title
        self.console = console or Console()
        self.file_extension = file_extension
        self.custom_scripts_path = custom_scripts_path
        self.used_examples = used_examples
        
        # Create FastAPI app
        self.app = FastAPI(title=title)
        
        # Set up templates
        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Set up static files
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        if self.custom_scripts_path:
            custom_dir = Path(self.custom_scripts_path).parent
            self.app.mount("/custom", StaticFiles(directory=str(custom_dir)), name="custom")

            self.console.print(f"[grey11]Mounted custom scripts at [bold cyan]{custom_dir}[/bold cyan][/grey11]")

        # Register routes
        self.app.get("/")(self.index)
        self.app.get("/js/{filename}")(self.serve_file)
        self.app.get("/api/files")(self.get_files)
        self.app.get("/api/file/{filename}")(self.serve_file)
        self.app.post("/api/select")(self.select_file)
        self.app.post("/api/feedback")(self.save_feedback)
        self.app.get("/api/feedback/{filename}")(self.get_feedback)
        self.app.post("/api/save-selected")(self.save_selected)
        self.app.post("/api/close")(self.close_viewer)
        self.app.get("/api/used-examples")(self.get_used_examples)
        self.app.get("/api/all-feedback")(self.get_all_feedback)
        self.console.print(f"[grey11]Initialized Viewer for [bold cyan]{self.concept or 'objects'}[/bold cyan][/grey11]")
    
    async def index(self, request: Request):
        """Render the main page."""
        return self.templates.TemplateResponse("index.html", {
            "request": request, 
            "concept": self.concept, 
            "title": self.title,
            "scripts_path": os.path.join("/custom", self.custom_scripts_path.split("/")[-1])
        })
    
    async def serve_file(self, filename: str):
        """Serve a file."""
        file_path = self.data_folder / filename
        if not file_path.exists():
            self.console.print(f"[bold red]File not found: {filename}[/bold red]")
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(str(file_path))
    
    async def get_files(self):
        """Get a list of all files in the folder with their content."""
        files = []
        for file in sorted(os.listdir(self.data_folder)):
            if file.lower().endswith(self.file_extension):
                file_path = self.data_folder / file
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    files.append({
                        'name': file,
                        'content': json.dumps(content)
                    })
                except Exception as e:
                    self.console.print(f"[bold red]Error reading {file}: {e}[/bold red]")
        self.console.print(f"[grey11]Rendering [bold cyan]{len(files)}[/bold cyan] files[/grey11]")
        return files
    
    async def select_file(self, data: Dict[str, Any]):
        """Select a file (only one at a time)."""
        file = data.get('file')
        
        if not file:
            self.console.print("[bold red]No file specified[/bold red]")
            raise HTTPException(status_code=400, detail="No file specified")
        
        self.selected_file = file
        return {"success": True, "selected": file}
    
    async def save_feedback(self, data: Dict[str, Any]):
        """Save feedback for a file."""
        file = data.get('file')
        feedback = data.get('feedback')
        
        if not file or not feedback:
            self.console.print("[bold red]File and feedback required[/bold red]")
            raise HTTPException(status_code=400, detail="File and feedback required")
        
        # Store feedback in memory
        if file not in self.feedback_data:
            self.feedback_data[file] = []
        
        self.feedback_data[file].append(feedback)
        self.console.print(f"[grey11]Saved feedback for [bold cyan]{file}[/bold cyan]: [grey11]{feedback[:50]}...[/grey11]")
        
        return {"success": True}
    
    async def get_feedback(self, filename: str):
        """Get feedback for a specific file."""
        if filename not in self.feedback_data:
            return {"feedback": []}
        
        return {"feedback": self.feedback_data[filename]}
    
    def get_all_feedback(self):
        """Get all feedback for all files."""
        return self.feedback_data
    
    async def save_selected(self, data: Dict[str, Any]):
        """Save the selected file to the output path."""
        file = self.selected_file
        
        if not file:
            self.console.print("[bold red]No file selected[/bold red]")
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not self.output_path:
            self.console.print("[bold red]No output path specified[/bold red]")
            raise HTTPException(status_code=400, detail="No output path specified")
        
        # Create output directory if it doesn't exist
        output_dir = Path(self.output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy selected file to the output path with concept name
        src_path = self.data_folder / file
        timestamp = int(time.time())
        concept_prefix = self.concept.replace(' ', '_') if self.concept else "object"
        dst_path = Path(self.output_path) / f"{concept_prefix}_{timestamp}{self.file_extension}"
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            self.console.print(f"[green]✓[/green] [grey11]Saved selected file to [bold cyan]{dst_path}[/bold cyan][/grey11]")
            return {"success": True, "path": str(dst_path)}
        else:
            self.console.print(f"[bold red]File not found: {src_path}[/bold red]")
            raise HTTPException(status_code=404, detail="File not found")
    
    async def get_used_examples(self):
        """Get the used examples."""
        if not self.used_examples:
            return {"used_examples": {}}
        
        used_examples = {}
        for file, feedbacks in self.used_examples.items():
            file_path = self.data_folder.parent / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = json.load(f)
                used_examples[file] = {
                    "content": content,
                    "feedback": feedbacks
                }
        
        return {"used_examples": used_examples}

    async def close_viewer(self):
        """Close the viewer and return the feedback."""
        self.server_running = False
        self.console.print("[grey11]Viewer closed[/grey11]")
        return {"success": True}
    
    def run(self, open_browser=True):
        """Run the FastAPI server and return the feedback when closed."""
        self.server_running = True
        
        # Start server in a separate thread
        def run_server():
            self.console.print(f"[grey11]Starting server on port [bold cyan]{self.port}[/bold cyan]...[/grey11]")
            uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="warning")
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Open browser if requested
        if open_browser:
            time.sleep(1.5)  # Give the server time to start
            url = f'http://localhost:{self.port}/'
            self.console.print(f"[grey11]Opening browser at [/grey11][link={url}]{url}[/link]")
            webbrowser.open(url)
        
        self.console.print("[green]Viewer is running. Close the browser window to continue.[/green]")
        
        # Wait for the server to stop
        while self.server_running:
            time.sleep(0.1)
        
        # Return the feedback data
        if self.feedback_data:
            self.console.print(f"[grey11]Collected feedback for [bold cyan]{len(self.feedback_data)}[/bold cyan] files[/grey11]")
        else:
            self.console.print("[grey11]No feedback collected, shutting down...[/grey11]")
        
        return self.feedback_data 
    
if __name__ == "__main__":
    viewer = Viewer(".data/examples/", ".data/examples/", "example", "Example Viewer", 8001)
    feedback_data = viewer.run()
    print(feedback_data)