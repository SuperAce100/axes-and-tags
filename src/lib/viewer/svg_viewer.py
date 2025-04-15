import os
import json
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

class SVGViewer:
    def __init__(self, svg_folder, output_path=None, port=8001, concept=None, title="SVG Viewer"):
        """
        Initialize the SVG viewer.
        
        Args:
            svg_folder (str): Path to the folder containing SVG files
            output_path (str, optional): Path to save the selected SVG
            port (int, optional): Port to run the server on
            concept (str, optional): Concept name for the output file
        """
        self.svg_folder = Path(svg_folder)
        self.output_path = output_path
        self.port = port
        self.selected_svg = None
        self.feedback_data = {}  # Map of SVG name to feedback
        self.server_running = False
        self.server_thread = None
        self.concept = concept
        self.title = title
        # Create FastAPI app
        self.app = FastAPI(title="SVG Viewer")
        
        # Set up templates
        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Set up static files
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Register routes
        self.app.get("/")(self.index)
        self.app.get("/svgs/{filename}")(self.serve_svg)
        self.app.get("/api/svgs")(self.get_svgs)
        self.app.post("/api/select")(self.select_svg)
        self.app.post("/api/feedback")(self.save_feedback)
        self.app.get("/api/feedback/{svg}")(self.get_feedback)
        self.app.post("/api/save-selected")(self.save_selected)
        self.app.post("/api/close")(self.close_viewer)
    
    async def index(self, request: Request):
        """Render the main page."""
        return self.templates.TemplateResponse("index.html", {"request": request, "concept": self.concept, "title": self.title})
    
    async def serve_svg(self, filename: str):
        """Serve an SVG file."""
        file_path = self.svg_folder / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="SVG file not found")
        return FileResponse(str(file_path))
    
    async def get_svgs(self):
        """Get a list of all SVG files in the folder with their content."""
        svg_files = []
        for file in os.listdir(self.svg_folder):
            if file.lower().endswith('.svg'):
                file_path = self.svg_folder / file
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    svg_files.append({
                        'name': file,
                        'content': content
                    })
                except Exception as e:
                    print(f"Error reading {file}: {e}")
        return svg_files
    
    async def select_svg(self, data: Dict[str, Any]):
        """Select an SVG (only one at a time)."""
        svg = data.get('svg')
        
        if not svg:
            raise HTTPException(status_code=400, detail="No SVG specified")
        
        self.selected_svg = svg
        return {"success": True, "selected": svg}
    
    async def save_feedback(self, data: Dict[str, Any]):
        """Save feedback for an SVG."""
        svg = data.get('svg')
        feedback = data.get('feedback')
        
        if not svg or not feedback:
            raise HTTPException(status_code=400, detail="SVG and feedback required")
        
        # Store feedback in memory
        if svg not in self.feedback_data:
            self.feedback_data[svg] = []
        
        self.feedback_data[svg].append(feedback)
        
        return {"success": True}
    
    async def get_feedback(self, svg: str):
        """Get feedback for a specific SVG."""
        if svg not in self.feedback_data:
            return {"feedback": []}
        
        return {"feedback": self.feedback_data[svg]}
    
    async def save_selected(self, data: Dict[str, Any]):
        """Save the selected SVG to the output path."""
        svg = self.selected_svg
        
        if not svg:
            raise HTTPException(status_code=400, detail="No SVG selected")
        
        if not self.output_path:
            raise HTTPException(status_code=400, detail="No output path specified")
        
        # Create output directory if it doesn't exist
        output_dir = Path(self.output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy selected SVG to the output path with concept.svg name
        src_path = self.svg_folder / svg
        dst_path = Path(self.output_path) / f"{self.concept}.svg"
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            return {"success": True, "path": str(dst_path)}
        else:
            raise HTTPException(status_code=404, detail="SVG file not found")
    
    async def close_viewer(self):
        """Close the viewer and return the feedback."""
        self.server_running = False
        return {"success": True}
    
    def run(self, open_browser=True):
        """Run the FastAPI server and return the feedback when closed."""
        self.server_running = True
        
        # Start server in a separate thread
        def run_server():
            uvicorn.run(self.app, host="0.0.0.0", port=self.port)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Open browser if requested
        if open_browser:
            time.sleep(1.5)  # Give the server time to start
            webbrowser.open(f'http://localhost:{self.port}/')
        
        # Wait for the server to stop
        while self.server_running:
            time.sleep(0.1)
        
        # Return the feedback data
        return self.feedback_data


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SVG Viewer')
    parser.add_argument('--folder', type=str, default='.data/flat/results/flower_1744669919_1221', help='Folder containing SVG files')
    parser.add_argument('--output', type=str, default='.data/flat/examples', help='Path to save the selected SVG')
    parser.add_argument('--port', type=int, default=8001, help='Port to run the server on')
    parser.add_argument('--concept', type=str, default='flower', help='Concept name')
    
    args = parser.parse_args()
    
    viewer = SVGViewer(args.folder, args.output, args.port, args.concept, f"{args.concept.capitalize()} in a flat style")
    feedback_data = viewer.run()
    print(f"Feedback data: {json.dumps(feedback_data, indent=2)}")
