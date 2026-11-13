"""
Image Pixelator - Python GUI with C++ Backend
Fast image pixelation with ROI selection support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
from PIL import Image, ImageTk, ImageDraw
import ctypes
import struct
import time
import json


# ============================================================
# C++ Backend Interface (loads pixelate.dll if available)
# Falls back to optimized Python implementation
# ============================================================

class PixelateEngine:
    """High-performance pixelation engine using PIL"""

    def __init__(self):
        pass

    def pixelate(self, image, block_size, x=0, y=0, w=None, h=None):
        """
        Pixelate image using PIL resize technique.
        If x,y,w,h are specified, only pixelate that region.
        image: PIL Image object (will be copied, not modified)
        block_size: size of each pixel block
        """
        if w is None:
            w = image.width
        if h is None:
            h = image.height

        if x == 0 and y == 0 and w == image.width and h == image.height:
            return self._pixelate_full(image, block_size)
        else:
            return self._pixelate_roi(image, block_size, x, y, w, h)

    def _pixelate_full(self, image, block_size):
        """Pixelate entire image using PIL resize-down-and-up technique"""
        img = image.convert('RGB')
        if block_size <= 1:
            return img

        new_w = max(1, img.width // block_size)
        new_h = max(1, img.height // block_size)
        pixelated = img.resize((new_w, new_h), Image.NEAREST)
        pixelated = pixelated.resize((img.width, img.height), Image.NEAREST)
        return pixelated

    def _pixelate_roi(self, image, block_size, x, y, w, h):
        """Pixelate only a region of interest"""
        img = image.convert('RGB').copy()
        pixels = img.load()
        end_x = min(x + w, img.width)
        end_y = min(y + h, img.height)

        for by in range(y, end_y, block_size):
            for bx in range(x, end_x, block_size):
                block_end_x = min(bx + block_size, end_x)
                block_end_y = min(by + block_size, end_y)
                block_w = block_end_x - bx
                block_h = block_end_y - by
                total_pixels = block_w * block_h

                sum_r = sum_g = sum_b = 0
                for py in range(by, block_end_y):
                    for px in range(bx, block_end_x):
                        r, g, b = pixels[px, py]
                        sum_r += r
                        sum_g += g
                        sum_b += b

                avg_r = sum_r // total_pixels
                avg_g = sum_g // total_pixels
                avg_b = sum_b // total_pixels

                for py in range(by, block_end_y):
                    for px in range(bx, block_end_x):
                        pixels[px, py] = (avg_r, avg_g, avg_b)

        return img


# ============================================================
# ROI Selection Tool
# ============================================================

class SelectionTool:
    """Interactive rectangle selection tool for ROI pixelation.
    Coordinates are in display/image pixel space (0,0 = top-left of image on canvas)."""

    def __init__(self, canvas, status_label, on_select):
        self.canvas = canvas
        self.status_label = status_label
        self.on_select = on_select
        self.start_x = None
        self.start_y = None
        self.selection_rect = None
        self.is_selecting = False
        self.image_width = 0
        self.image_height = 0

        # Clear any existing bindings first
        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def set_image(self, image_width, image_height):
        """Set image dimensions for bounds checking"""
        self.image_width = image_width
        self.image_height = image_height

    def on_press(self, event):
        if event.x < 0 or event.y < 0:
            return

        if self.image_width == 0 or self.image_height == 0:
            return

        if event.x >= self.image_width or event.y >= self.image_height:
            return

        self.start_x = event.x
        self.start_y = event.y
        self.is_selecting = True

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

    def on_drag(self, event):
        if not self.is_selecting:
            return

        x = max(0, min(event.x, self.image_width))
        y = max(0, min(event.y, self.image_height))

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        self.selection_rect = self.canvas.create_rectangle(
            min(self.start_x, x),
            min(self.start_y, y),
            max(self.start_x, x),
            max(self.start_y, y),
            outline='red', width=2, dash=(4, 4)
        )

        sel_w = abs(x - self.start_x)
        sel_h = abs(y - self.start_y)
        self.status_label.config(text=f"Selection: {sel_w} x {sel_h} pixels")

    def on_release(self, event):
        if not self.is_selecting:
            return

        self.is_selecting = False

        if self.start_x is None or self.start_y is None:
            return

        x = max(0, min(event.x, self.image_width))
        y = max(0, min(event.y, self.image_height))

        sel_x = int(min(self.start_x, x))
        sel_y = int(min(self.start_y, y))
        sel_w = int(abs(x - self.start_x))
        sel_h = int(abs(y - self.start_y))

        if sel_w < 5 or sel_h < 5:
            self.status_label.config(text="Selection too small - click and drag again")
            return

        if self.on_select:
            self.on_select(sel_x, sel_y, sel_w, sel_h)


# ============================================================
# Main Application GUI
# ============================================================

class PixelatorApp:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Image Pixelator")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.engine = PixelateEngine()
        self.base_image = None        # The current working image (original or processed)
        self.original_image = None    # The very first loaded image (for reset)
        self.selection = None         # (x, y, w, h) in original image coords
        self.selection_tool = None
        self.display_image = None     # PIL Image scaled for display
        self.tk_image = None          # tkinter PhotoImage
        self.image_w = 0              # Display width in pixels
        self.image_h = 0              # Display height in pixels

        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        """Build the UI layout"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # File operations
        file_frame = ttk.LabelFrame(control_frame, text="File", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(file_frame, text="Open Image", command=self.open_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Save Result", command=self.save_image).pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Reset", command=self.reset_image).pack(fill=tk.X, pady=2)

        # Pixelation settings
        settings_frame = ttk.LabelFrame(control_frame, text="Pixelation", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(settings_frame, text="Block Size:").pack(anchor=tk.W)

        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=2)

        self.block_size_var = tk.StringVar(value="16")
        self.block_size_slider = ttk.Scale(
            size_frame, from_=2, to=64,
            variable=self.block_size_var, orient=tk.HORIZONTAL
        )
        self.block_size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.block_size_label = ttk.Label(size_frame, text="16", width=4)
        self.block_size_label.pack(side=tk.LEFT, padx=(5, 0))
        self.block_size_slider.config(command=self._update_block_size_label)

        # ROI mode
        roi_frame = ttk.LabelFrame(control_frame, text="Region Selection", padding=5)
        roi_frame.pack(fill=tk.X, pady=(0, 10))

        self.roi_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            roi_frame, text="Enable ROI mode",
            variable=self.roi_mode_var, command=self._toggle_roi_mode
        ).pack(anchor=tk.W, pady=2)

        self.roi_info_label = ttk.Label(
            roi_frame, text="Click on image to select region",
            foreground='gray'
        )
        self.roi_info_label.pack(anchor=tk.W, pady=2)

        # Preset sizes
        preset_frame = ttk.LabelFrame(control_frame, text="Presets", padding=5)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        preset_buttons = [
            ("Subtle (8)", 8), ("Medium (16)", 16),
            ("Strong (32)", 32), ("Extreme (64)", 64)
        ]
        preset_row = ttk.Frame(preset_frame)
        preset_row.pack(fill=tk.X)
        for name, size in preset_buttons:
            ttk.Button(preset_row, text=name,
                       command=lambda s=size: self._set_block_size(s)).pack(side=tk.LEFT, padx=2)

        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(action_frame, text="Apply Pixelation",
                   command=self.apply_pixelation, style="Accent.TButton").pack(
            fill=tk.X, pady=5)

        # Right panel - Image display
        image_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding=5)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(image_frame, bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.status_frame, text="No image loaded - Open an image to begin")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

    def _setup_bindings(self):
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-r>', lambda e: self.reset_image())
        self.root.bind('<Control-p>', lambda e: self.apply_pixelation())

    def _update_block_size_label(self, value):
        self.block_size_label.config(text=str(int(float(value))))

    def _set_block_size(self, size):
        self.block_size_var.set(str(size))
        self.block_size_label.config(text=str(size))
        self.block_size_slider.set(size)

    def _toggle_roi_mode(self):
        if self.roi_mode_var.get():
            if not self.base_image:
                self.roi_mode_var.set(False)
                self.roi_info_label.config(text="No image loaded", foreground='gray')
                return
            self.roi_info_label.config(text="Click and drag on image to select region", foreground='black')
            self._create_selection_tool()
        else:
            self.roi_info_label.config(text="ROI mode disabled - full image pixelation", foreground='gray')
            self.selection = None
            self.selection_tool = None
            # Clear selection rectangle from canvas
            if self.canvas:
                self.canvas.delete('selection_rect')
            self.status_label.config(text="ROI mode disabled")

    def _create_selection_tool(self):
        """Create or recreate the selection tool"""
        if not self.base_image or self.image_w == 0 or self.image_h == 0:
            return

        self.selection_tool = SelectionTool(
            self.canvas,
            self.status_label,
            on_select=self._on_region_selected
        )
        self.selection_tool.set_image(self.image_w, self.image_h)

    def _on_region_selected(self, x, y, w, h):
        """Handle ROI selection - convert display coordinates to base image coordinates"""
        scale_x = self.image_w / self.base_image.width if self.base_image.width > 0 else 1
        scale_y = self.image_h / self.base_image.height if self.base_image.height > 0 else 1

        orig_x = int(x / scale_x)
        orig_y = int(y / scale_y)
        orig_w = int(w / scale_x)
        orig_h = int(h / scale_y)

        # Clamp to image bounds
        orig_x = max(0, orig_x)
        orig_y = max(0, orig_y)
        orig_w = min(orig_w, self.base_image.width - orig_x)
        orig_h = min(orig_h, self.base_image.height - orig_y)

        self.selection = (orig_x, orig_y, orig_w, orig_h)
        self.status_label.config(
            text=f"Region selected: ({orig_x}, {orig_y}) {orig_w}x{orig_h} pixels"
        )

    def open_image(self):
        """Open an image file"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
            ("All files", "*.*")
        ]

        filepath = filedialog.askopenfilename(
            title="Open Image",
            filetypes=filetypes
        )

        if not filepath:
            return

        try:
            img = Image.open(filepath)
            self.original_image = img.copy()
            self.base_image = img.copy()
            self.selection = None
            self.selection_tool = None
            self.roi_mode_var.set(False)

            self.roi_info_label.config(
                text="Click and drag on image to select region", foreground='gray'
            )
            self._display_image(self.base_image)

            self.status_label.config(
                text=f"Loaded: {filepath} | Size: {img.size[0]}x{img.size[1]} | Mode: {img.mode}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")

    def _display_image(self, image):
        """Display image on canvas with proper scaling.
        Image is drawn at canvas (0,0) so mouse coordinates map directly."""
        self.canvas.delete(tk.ALL)

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            self.root.after(100, lambda: self._display_image(image))
            return

        padding = 40
        available_w = canvas_w - padding
        available_h = canvas_h - padding

        img_w, img_h = image.size
        scale = min(available_w / img_w, available_h / img_h, 1.0)

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        self.image_w = new_w
        self.image_h = new_h
        self.display_image = image.resize((new_w, new_h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=new_w, height=new_h, bg='#1a1a1a')
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Recreate selection tool if ROI mode is active
        if self.roi_mode_var.get():
            self._create_selection_tool()

        self.status_label.config(
            text=f"Display: {new_w}x{new_h} | Scale: {scale:.2f}x"
        )

    def apply_pixelation(self):
        """Apply pixelation to the current base image"""
        if not self.base_image:
            messagebox.showwarning("Warning", "Please open an image first.")
            return

        block_size = int(float(self.block_size_var.get()))

        if block_size < 2:
            messagebox.showerror("Error", "Block size must be at least 2.")
            return

        self.progress.start()
        self.status_label.config(text="Processing...")

        def process():
            try:
                if self.roi_mode_var.get() and self.selection:
                    x, y, w, h = self.selection
                    result = self.engine.pixelate(
                        self.base_image, block_size, x, y, w, h
                    )
                else:
                    result = self.engine.pixelate(
                        self.base_image, block_size
                    )

                # Update base_image for subsequent operations
                self.base_image = result
                self.root.after(0, lambda: self._after_processing())

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self._processing_error(str(e)))

        threading.Thread(target=process, daemon=True).start()

    def _after_processing(self):
        """Handle successful processing"""
        self.progress.stop()
        self._display_image(self.base_image)
        self.status_label.config(text="Pixelation applied successfully")

    def _processing_error(self, error):
        """Handle processing error"""
        self.progress.stop()
        messagebox.showerror("Error", f"Processing failed:\n{error}")
        self.status_label.config(text="Processing failed")

    def save_image(self):
        """Save the current image (processed or original)"""
        if not self.base_image:
            messagebox.showwarning("Warning", "No image to save.")
            return

        image_to_save = self.base_image

        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=filetypes
        )

        if not filepath:
            return

        try:
            if filepath.lower().endswith(('.jpg', '.jpeg')):
                image_to_save = image_to_save.convert('RGB')

            image_to_save.save(filepath)
            self.status_label.config(text=f"Saved: {filepath}")
            messagebox.showinfo("Success", f"Image saved to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

    def reset_image(self):
        """Reset to the original loaded image"""
        if not self.original_image:
            return

        self.base_image = self.original_image.copy()
        self.selection = None
        self.selection_tool = None
        self.roi_mode_var.set(False)
        self.roi_info_label.config(text="Click and drag on image to select region", foreground='gray')
        self._display_image(self.base_image)
        self.status_label.config(text="Image reset to original")


# ============================================================
# Entry Point
# ============================================================

def main():
    root = tk.Tk()

    try:
        style = ttk.Style()
        style.theme_use('vista')
    except Exception:
        try:
            style = ttk.Style()
            style.theme_use('clam')
        except Exception:
            pass

    app = PixelatorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
