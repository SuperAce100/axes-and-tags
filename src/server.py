import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import argparse
from designgalleries import generate
from designspace import DesignSpace, Generation, Tag, Example
from domains.domain import Domain
from domains.imagegen.imagegen import ImageGen
from models.llms import text_model
from typing import List
from rich.console import Console
class StartRequest(BaseModel):
    concept: str
    domain: str

class GenerateRequest(BaseModel):
    concept: str
    domain: str
    design_space: DesignSpace | None = None

class GenerateResponse(BaseModel):
    design_space: DesignSpace
    generations: List[Example]

class DomainResponse(BaseModel):
    name: str
    display_name: str

class Server:
    def __init__(self, 
                 domains: List[Domain], 
                 n: int, 
                 model: str = text_model,
                 console: Console = None):
        self.app = FastAPI()
        self.domains = domains
        self.n = n
        self.model = model
        self.console = console

        templates_dir = Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(templates_dir))

        self.static_dir = Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")

        self.app.get("/")(self.start_page)
        self.app.get("/generated/{domain}/{concept}")(self.generated_page)

        #########################################################
        self.app.get("/api/domains")(self.get_domains)
        self.app.post("/api/generate")(self.generate)


        self.generations: List[(DesignSpace, List[Generation])] = []


    #########################################################
    # HTML endpoints
    #########################################################

    async def start_page(self, request: Request):
        return self.templates.TemplateResponse("index.html", {"request": request})
    
    async def generated_page(self, request: Request, domain: str, concept: str):
        domain = next((d for d in self.domains if d.name == domain), None)
        if domain is None:
            return HTTPException(status_code=404, detail="Domain not found")
        
        custom_scripts_path = domain.scripts_path
        self.app.mount("/custom", StaticFiles(directory=str(Path(custom_scripts_path).parent)), name="custom")
        
        return self.templates.TemplateResponse("generated.html", {"request": request, "domain_name": domain.display_name, "scripts_path": os.path.join("/custom", custom_scripts_path.split("/")[-1]), "concept": concept})
    
    #########################################################
    # API endpoints
    #########################################################

    async def get_domains(self) -> List[DomainResponse]:
        return [DomainResponse(name=d.name, display_name=d.display_name) for d in self.domains]

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        domain = next((d for d in self.domains if d.name == request.domain), None)
        if domain is None:
            return HTTPException(status_code=404, detail="Domain not found")
        
        print("request.design_space", request.design_space)
        
        if len(self.generations) > 0 and request.design_space == self.generations[-1][0]:
            return GenerateResponse(design_space=request.design_space, generations=self.generations[-1][1])
        
        design_space = request.design_space
        if design_space is None:
            design_space = DesignSpace.create(request.concept, domain.display_name)

        design_space.explore_new_axis()
        design_space.fill()

        generations = generate(request.concept, design_space, domain=domain, n=self.n, model=self.model, console=self.console)

        self.generations.append((design_space, generations))
        return GenerateResponse(design_space=design_space, generations=generations)

    def run(self, reload: bool = False, port: int = 8000):
        uvicorn.run(self.app, host="0.0.0.0", port=port, reload=reload)

def parse_args():
    parser = argparse.ArgumentParser(description='Run FastAPI server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--n', type=int, default=6, help='Number of layouts to generate')
    parser.add_argument('--reload', action='store_true', help='Enable hot reload')
    parser.add_argument('--data-dir', type=str, default="../.data", help='Data directory')
    parser.add_argument('--model', type=str, default=text_model, help='Model to use')
    parser.add_argument('--cerebras', action='store_true', help='Use Cerebras model')
    return parser.parse_args()

def main():
    args = parse_args()
    console = Console()
    if args.cerebras:
        model = "cerebras"
    else:
        model = args.model

    domains = [ImageGen(data_dir=args.data_dir, console=console, model=model)]

    server = Server(n=args.n, domains=domains, model=model)
    server.run(reload=False, port=args.port)

if __name__ == "__main__":
    main()