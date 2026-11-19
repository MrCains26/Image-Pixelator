"""
Image display on the main canvas, with scaling.
"""

from PIL import Image, ImageTk

import tkinter as tk


class ImageDisplay:

    def __init__(self, app_ref):
        self.app = app_ref

    def display(self, image):
        self.app.canvas.delete(tk.ALL)

        canvas_w = self.app.canvas.winfo_width()
        canvas_h = self.app.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            self.app.root.after(100, lambda: self.display(image))
            return

        padding = 40
        available_w = canvas_w - padding
        available_h = canvas_h - padding

        img_w, img_h = image.size
        scale = min(available_w / img_w, available_h / img_h, 1.0)

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        self.app.image_w = new_w
        self.app.image_h = new_h
        self.app.display_image = image.resize((new_w, new_h), Image.LANCZOS)
        self.app.tk_image = ImageTk.PhotoImage(self.app.display_image)

        self.app.canvas.config(width=new_w, height=new_h, bg='#1a1a1a')
        self.app.canvas.create_image(0, 0, anchor=tk.NW, image=self.app.tk_image)

        if self.app.roi_mode_var.get():
            self.app._create_selection_tool()

        self.app.status_label.config(
            text=f"Display: {new_w}x{new_h} | Scale: {scale:.2f}x"
        )
