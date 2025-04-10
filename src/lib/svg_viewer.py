import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cairosvg
import io
from pathlib import Path
import sys
import os
import shutil



class SVGViewer:
    def __init__(self, root, svg_path, save_path=None):
        self.root = root
        self.root.title("SVG Viewer")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)  # Set minimum window size

        self.svg_path = Path(svg_path)
        self.save_path = Path(save_path) if save_path else None
        self.svg_files = list(self.svg_path.glob("*.svg"))
        self.current_index = 0

        self.setup_ui()
        self.setup_keyboard_shortcuts()
        # Wait for window to be ready
        self.root.update()
        self.load_current_svg()

    def setup_ui(self):
        # Theming
        s = ttk.Style()
        s.theme_use("clam")

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # SVG display area
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Button(self.main_frame, text="Previous (←)", command=self.prev_svg).grid(
            row=1, column=0, pady=10
        )
        ttk.Button(self.main_frame, text="Next (→)", command=self.next_svg).grid(
            row=1, column=1, pady=10
        )
        ttk.Button(self.main_frame, text="Save (s)", command=self.save_svg).grid(
            row=1, column=2, pady=10
        )

        self.counter_label = ttk.Label(self.main_frame, text="")
        self.counter_label.grid(row=2, column=0, columnspan=3, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.root.bind("<Configure>", self.on_window_resize)

    def setup_keyboard_shortcuts(self):
        self.root.bind("<Left>", lambda e: self.prev_svg())
        self.root.bind("<Right>", lambda e: self.next_svg())
        self.root.bind("s", lambda e: self.save_svg())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def on_window_resize(self, event):
        if event.widget == self.root:
            self.load_current_svg()

    def load_current_svg(self):
        if not self.svg_files:
            messagebox.showinfo(
                "No SVGs", "No SVG files found in the specified directory"
            )
            return

        svg_file = self.svg_files[self.current_index]

        png_data = cairosvg.svg2png(url=str(svg_file))

        image = Image.open(io.BytesIO(png_data))

        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())

        width_ratio = canvas_width / image.width
        height_ratio = canvas_height / image.height
        scale = min(width_ratio, height_ratio) * 0.9

        new_width = max(1, int(image.width * scale))
        new_height = max(1, int(image.height * scale))

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2, image=self.photo, anchor=tk.CENTER
        )

        self.counter_label.config(
            text=f"File {self.current_index + 1} of {len(self.svg_files)}: {svg_file.name}"
        )

    def next_svg(self):
        self.current_index = (self.current_index + 1) % len(self.svg_files)
        self.load_current_svg()

    def prev_svg(self):
        self.current_index = (self.current_index - 1) % len(self.svg_files)
        self.load_current_svg()

    def save_svg(self):
        if not self.svg_files:
            return

        if self.save_path:
            save_dir = self.save_path
        else:
            save_dir = filedialog.askdirectory(title="Select Save Directory")
            if save_dir:
                self.save_path = Path(save_dir)

        if save_dir:
            current_svg = self.svg_files[self.current_index]
            save_path = Path(save_dir) / current_svg.name
            os.makedirs(save_path.parent, exist_ok=True)

            try:
                shutil.copy2(current_svg, save_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")


def main():
    root = tk.Tk()


    svg_path = sys.argv[1] if len(sys.argv) > 1 else "."
    save_path = sys.argv[2] if len(sys.argv) > 2 else None
    SVGViewer(root, svg_path, save_path)
    root.mainloop()


if __name__ == "__main__":
    main()
