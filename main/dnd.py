"""
Drag-and-drop file handling using tkinterdnd2.
"""

import os

import tkinterdnd2

from PIL import Image


class DragDropHandler:

    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp'}

    def __init__(self, root_ref, app_ref):
        self.root = root_ref
        self.app = app_ref

    def setup(self):
        self.root.drop_target_register(tkinterdnd2.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        data = event.data

        files = []
        if isinstance(data, (tuple, list)):
            files = list(data)
        elif isinstance(data, str):
            try:
                files = self.root.tk.splitlist(data)
            except Exception:
                parts = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                files = [p.strip().strip('"').strip("'") for p in parts if p.strip()]

        dropped_images = []
        for f in files:
            f = f.strip().strip('"').strip("'")
            f = f.replace('/', '\\')
            ext = os.path.splitext(f)[1].lower()
            if ext in self.IMAGE_EXTENSIONS and os.path.isfile(f):
                dropped_images.append(f)

        if not dropped_images:
            return tkinterdnd2.REFUSE_DROP

        start_idx = len(self.app.images)
        for idx, filepath in enumerate(dropped_images):
            img = Image.open(filepath)
            actual_idx = start_idx + idx
            self.app.images.append(img)
            self.app.image_paths.append(filepath)
            self.app.image_states[actual_idx] = {'original': img.copy(), 'processed': None, 'roi': []}

        self.app.selected_index = start_idx
        self.app._load_selected_image()
        self.app._update_thumbnail_bar()
        self.app._update_status()
        self.app._update_button_states()
        self.app.status_label.config(
            text=f"Loaded {len(dropped_images)} image(s) via drag-and-drop"
        )
        return tkinterdnd2.COPY
