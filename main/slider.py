"""
Block size slider UI and logic.
"""

import tkinter as tk


class BlockSizeSlider:

    def __init__(self, parent_frame, entry_frame, var):
        self.var = var
        self.slider_frame = None
        self.canvas = None
        self.entry = None
        self._setup(parent_frame, entry_frame)

    def _setup(self, parent_frame, entry_frame):
        ttk = parent_frame.__class__.__bases__[0]
        from tkinter import ttk

        preset_label = ttk.Label(parent_frame, text="Presets:")
        preset_label.pack(anchor=tk.W, pady=(8, 2))
        preset_buttons = [
            ("Subtle (8)", 8), ("Medium (16)", 16),
            ("Strong (32)", 32), ("Extreme (64)", 64)
        ]
        preset_row = ttk.Frame(parent_frame)
        preset_row.pack(fill=tk.X, pady=2)
        for name, size in preset_buttons:
            ttk.Button(preset_row, text=name,
                       command=lambda s=size: self._set_block_size(s)).pack(side=tk.LEFT, padx=2)

        self.slider_frame = ttk.Frame(entry_frame)
        self.slider_frame.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.canvas = tk.Canvas(
            self.slider_frame, height=20,
            bg='#e8e8e8', highlightthickness=0,
            takefocus=1
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.entry = tk.Entry(entry_frame, textvariable=self.var, width=4,
                              justify='center', bg='#ffffff', fg='#000000',
                              relief='solid', borderwidth=1)
        self.entry.pack(side=tk.LEFT, padx=(5, 0))

        self.canvas.bind('<Configure>', lambda e: self._draw_slider())
        self.canvas.bind('<B1-Motion>', self._on_slider_click)
        self.canvas.bind('<ButtonPress-1>', self._on_canvas_click)
        self.slider_frame.bind('<ButtonPress-1>', self._on_slider_frame_click)

    def _set_block_size(self, size):
        self.var.set(str(size))
        self._draw_slider()

    def _validate_block_size(self):
        try:
            value = int(self.var.get())
            value = max(2, min(64, value))
            self.var.set(str(value))
            self._draw_slider()
        except (ValueError, tk.TclError):
            self.var.set("16")
            self._draw_slider()

    def _draw_slider(self):
        self.canvas.delete(tk.ALL)

        canvas_w = self.canvas.winfo_width()
        if canvas_w < 10 or self.canvas.winfo_ismapped() == 0:
            self.canvas.after(100, self._draw_slider)
            return

        val = self.var.get()
        try:
            size = int(float(val))
        except (ValueError, TypeError):
            size = 16
        size = max(2, min(64, size))

        padding = 8
        usable_w = max(1, canvas_w - 2 * padding)

        frac = (size - 2) / (64 - 2)
        thumb_x = padding + frac * usable_w
        thumb_w = 12

        self.canvas.create_rectangle(
            0, 6, canvas_w, 14,
            fill='#c0c0c0', outline='',
            tags='track'
        )

        self.canvas.create_rectangle(
            0, 6, int(thumb_x), 14,
            fill='#4a90d9', outline='',
            tags='fill'
        )

        self.canvas.create_rectangle(
            thumb_x - thumb_w//2, 3,
            thumb_x + thumb_w//2, 17,
            fill='#ffffff', outline='#888888',
            tags='thumb'
        )

    def _on_slider_click(self, event):
        w = self.canvas.winfo_width()
        if w <= 1:
            return
        padding = 8
        usable_w = max(1, w - 2 * padding)
        click_x = max(padding, min(event.x, w - padding))
        frac = (click_x - padding) / usable_w
        value = 2 + frac * (64 - 2)
        value = int(round(value))
        value = max(2, min(64, value))
        self.var.set(str(value))

    def _on_canvas_click(self, event):
        self._validate_block_size()
        self._on_slider_click(event)

    def _on_slider_frame_click(self, event):
        self._validate_block_size()
        self._on_slider_click(event)

    def get_value(self):
        try:
            return int(self.var.get())
        except (ValueError, tk.TclError):
            return 16
