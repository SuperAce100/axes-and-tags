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

class ThreeJSViewer:
    def __init__(self, js_folder, output_path=None, concept=None, title="3D Object Viewer", port=8001, console=None):
        """
        Initialize the Three.js viewer.
        
        Args:
            js_folder (str): Path to the folder containing Three.js files
            output_path (str, optional): Path to save the selected object
            port (int, optional): Port to run the server on
            concept (str, optional): Concept name for the output file
            console (Console, optional): Rich console for output
        """
        self.js_folder = Path(js_folder)
        self.output_path = output_path
        self.port = port
        self.selected_js = None
        self.feedback_data = {}  # Map of JS name to feedback
        self.server_running = False
        self.server_thread = None
        self.concept = concept
        self.title = title
        self.console = console or Console()
        
        # Create FastAPI app
        self.app = FastAPI(title="Three.js Viewer")
        
        # Set up templates
        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Set up static files
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Register routes
        self.app.get("/")(self.index)
        self.app.get("/js/{filename}")(self.serve_js)
        self.app.get("/api/js")(self.get_js_files)
        self.app.get("/api/dsl/{filename}")(self.serve_dsl)
        self.app.post("/api/select")(self.select_js)
        self.app.post("/api/feedback")(self.save_feedback)
        self.app.get("/api/feedback/{js}")(self.get_feedback)
        self.app.post("/api/save-selected")(self.save_selected)
        self.app.post("/api/close")(self.close_viewer)
        
        self.console.print(f"[grey11]Initialized ThreeJS Viewer for [bold cyan]{self.concept or 'objects'}[/bold cyan][/grey11]")
    
    async def index(self, request: Request):
        """Render the main page."""
        return self.templates.TemplateResponse("threejs_index.html", {"request": request, "concept": self.concept, "title": self.title})
    
    async def serve_js(self, filename: str):
        """Serve a JavaScript file."""
        file_path = self.js_folder / filename
        if not file_path.exists():
            self.console.print(f"[bold red]JavaScript file not found: {filename}[/bold red]")
            raise HTTPException(status_code=404, detail="JavaScript file not found")
        return FileResponse(str(file_path))
    
    async def serve_dsl(self, filename: str):
        """Serve a DSL file."""
        file_path = self.js_folder / filename
        if not file_path.exists():
            self.console.print(f"[bold red]DSL file not found: {filename}[/bold red]")
            raise HTTPException(status_code=404, detail="DSL file not found")
        return FileResponse(str(file_path))
    
    async def get_js_files(self):
        """Get a list of all DSL files in the folder with their content."""
        dsl_files = []
        for file in sorted(os.listdir(self.js_folder)):
            if file.lower().endswith('.dsl'):
                file_path = self.js_folder / file
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    dsl_files.append({
                        'name': file,
                        'content': content
                    })
                except Exception as e:
                    self.console.print(f"[bold red]Error reading {file}: {e}[/bold red]")
        self.console.print(f"[grey11]Found [bold cyan]{len(dsl_files)}[/bold cyan] DSL files[/grey11]")
        return dsl_files
    
    async def select_js(self, data: Dict[str, Any]):
        """Select a JavaScript file (only one at a time)."""
        js = data.get('js')
        
        if not js:
            self.console.print("[bold red]No JavaScript file specified[/bold red]")
            raise HTTPException(status_code=400, detail="No JavaScript file specified")
        
        self.selected_js = js
        return {"success": True, "selected": js}
    
    async def save_feedback(self, data: Dict[str, Any]):
        """Save feedback for a JavaScript file."""
        js = data.get('js')
        feedback = data.get('feedback')
        
        if not js or not feedback:
            self.console.print("[bold red]JavaScript file and feedback required[/bold red]")
            raise HTTPException(status_code=400, detail="JavaScript file and feedback required")
        
        # Store feedback in memory
        if js not in self.feedback_data:
            self.feedback_data[js] = []
        
        self.feedback_data[js].append(feedback)
        self.console.print(f"[grey11]Saved feedback for [bold cyan]{js}[/bold cyan]: [grey11]{feedback[:50]}...[/grey11]")
        
        return {"success": True}
    
    async def get_feedback(self, js: str):
        """Get feedback for a specific JavaScript file."""
        if js not in self.feedback_data:
            return {"feedback": []}
        
        return {"feedback": self.feedback_data[js]}
    
    async def save_selected(self, data: Dict[str, Any]):
        """Save the selected JavaScript file to the output path."""
        js = self.selected_js
        
        if not js:
            self.console.print("[bold red]No JavaScript file selected[/bold red]")
            raise HTTPException(status_code=400, detail="No JavaScript file selected")
        
        if not self.output_path:
            self.console.print("[bold red]No output path specified[/bold red]")
            raise HTTPException(status_code=400, detail="No output path specified")
        
        # Create output directory if it doesn't exist
        output_dir = Path(self.output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy selected JavaScript file to the output path with concept.js name
        src_path = self.js_folder / js
        timestamp = int(time.time())
        dst_path = Path(self.output_path) / f"{self.concept.replace(' ', '_')}_{timestamp}.dsl"
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            self.console.print(f"[green]✓[/green] [grey11]Saved selected file to [bold cyan]{dst_path}[/bold cyan][/grey11]")
            return {"success": True, "path": str(dst_path)}
        else:
            self.console.print(f"[bold red]JavaScript file not found: {src_path}[/bold red]")
            raise HTTPException(status_code=404, detail="JavaScript file not found")
    
    async def close_viewer(self):
        """Close the viewer and return the feedback."""
        self.server_running = False
        self.console.print("[yellow]Viewer closed[/yellow]")
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
            self.console.print("[red]No feedback collected[/red]")
        
        return self.feedback_data 
    
if __name__ == "__main__":
    viewer = ThreeJSViewer(".data/dormroom/examples/", ".data/dormroom/examples/", "dorm", "Dorm Room Viewer", 8001)
    feedback_data = viewer.run()
    print(feedback_data)