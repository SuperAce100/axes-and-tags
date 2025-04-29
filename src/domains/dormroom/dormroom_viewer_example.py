import os
import argparse
from pathlib import Path
from rich.console import Console

from src.domains.dormroom.dormroom_viewer import DormRoomViewer

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DormRoom Viewer Example')
    parser.add_argument('--data-dir', type=str, default='.data/dormroom/examples', 
                        help='Directory containing DSL files')
    parser.add_argument('--output-dir', type=str, default='.data/dormroom/examples/selected', 
                        help='Directory to save selected files')
    parser.add_argument('--port', type=int, default=8001, 
                        help='Port to run the server on')
    args = parser.parse_args()
    
    console = Console()
    
    # Create directories if they don't exist
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some example DSL files
    example_files = [
        ("dorm1.dsl", """
layout:
  name: "Standard Dorm"
  type: "dorm"
  width: 400
  length: 600
  height: 300
  furniture:
    - item: "bed"
      position: [50, 50]
      rotation: 0
      size: [200, 100]
    - item: "desk"
      position: [300, 100]
      rotation: 0
      size: [120, 60]
    - item: "chair"
      position: [300, 200]
      rotation: 0
      size: [50, 50]
    - item: "wardrobe"
      position: [50, 500]
      rotation: 0
      size: [100, 60]
"""),
        ("dorm2.dsl", """
layout:
  name: "Luxury Dorm"
  type: "dorm"
  width: 500
  length: 700
  height: 350
  furniture:
    - item: "bed"
      position: [100, 100]
      rotation: 0
      size: [220, 120]
    - item: "desk"
      position: [350, 150]
      rotation: 0
      size: [150, 70]
    - item: "chair"
      position: [350, 250]
      rotation: 0
      size: [60, 60]
    - item: "wardrobe"
      position: [100, 600]
      rotation: 0
      size: [120, 70]
    - item: "sofa"
      position: [400, 500]
      rotation: 90
      size: [180, 80]
"""),
        ("dorm3.dsl", """
layout:
  name: "Compact Dorm"
  type: "dorm"
  width: 300
  length: 400
  height: 250
  furniture:
    - item: "bed"
      position: [50, 50]
      rotation: 0
      size: [180, 90]
    - item: "desk"
      position: [200, 100]
      rotation: 0
      size: [100, 50]
    - item: "chair"
      position: [200, 200]
      rotation: 0
      size: [40, 40]
    - item: "wardrobe"
      position: [50, 350]
      rotation: 0
      size: [80, 50]
""")
    ]
    
    for filename, content in example_files:
        file_path = data_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
    
    # Initialize the viewer
    viewer = DormRoomViewer(
        js_folder=str(data_dir),
        output_path=str(output_dir),
        concept="dorm",
        title="Dorm Room Viewer",
        port=args.port,
        console=console
    )
    
    # Run the viewer
    feedback_data = viewer.run()
    
    # Print the feedback data
    console.print(feedback_data)

if __name__ == "__main__":
    main() 