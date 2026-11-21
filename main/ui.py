import tkinter as tk
from tkinter import ttk

from slider import BlockSizeSlider


class UILayout:

    def __init__(self, app_ref):
        self.app = app_ref

    def setup(self):
        self._setup_menu_bar()
        self._setup_main_layout()
        self._setup_pixelation_settings()
        self._build_roi_settings()
        self._setup_action_buttons()
        self._setup_status_bar()

    def _setup_menu_bar(self):
        self.app.menu_bar = ttk.Frame(self.app.root, style="Menu.TFrame")
        self.app.menu_bar.pack(fill=tk.X, side=tk.TOP)

        self.app.settings_btn = ttk.Button(
            self.app.menu_bar,
            text="Settings",
            command=self.app.settings.toggle
        )
        self.app.settings_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def _setup_main_layout(self):
        main_frame = ttk.Frame(self.app.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.app.main_frame = main_frame
        self.app.control_frame = ttk.LabelFrame(main_frame, text="Image Settings", padding=10)
        self.app.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        image_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding=5)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.app.image_frame = image_frame

        file_frame = ttk.LabelFrame(self.app.control_frame, text="File", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        open_frame = ttk.Frame(file_frame)
        open_frame.pack(fill=tk.X, pady=2)
        self.app.open_image_btn = ttk.Button(open_frame, text="Open Image", command=self.app.file_ops.open_image)
        self.app.open_image_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.app.open_folder_btn = ttk.Button(open_frame, text="Open Folder", command=self.app.file_ops.open_folder)
        self.app.open_folder_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        download_frame = ttk.Frame(file_frame)
        download_frame.pack(fill=tk.X, pady=2)
        self.app.download_this_btn = ttk.Button(download_frame, text="Download This Image", command=self.app.file_ops.save_image)
        self.app.download_this_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.app.download_all_btn = ttk.Button(download_frame, text="Download All Images", command=self.app.file_ops.download_all)
        self.app.download_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        self.app.reset_frame = ttk.Frame(file_frame)
        self.app.reset_frame.pack(fill=tk.X, pady=(2, 0))
        self.app.reset_btn = ttk.Button(self.app.reset_frame, text="Reset Edits (This Image)", command=self.app.file_ops.reset_image)
        self.app.reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.app.reset_all_btn = ttk.Button(self.app.reset_frame, text="Reset Edits (All Images)", command=self.app.file_ops.reset_all_images)
        self.app.reset_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        self.app.thumb_bar_frame = ttk.Frame(image_frame)
        self.app.thumb_bar_frame.pack(fill=tk.X, padx=2, pady=(0, 2))

        clear_bar = ttk.Frame(self.app.thumb_bar_frame)
        clear_bar.pack(fill=tk.X, pady=(0, 2))
        self.app.clear_all_btn = ttk.Button(clear_bar, text="Clear All Images", command=self.app.file_ops.clear_all)
        self.app.clear_all_btn.pack(side=tk.LEFT)

        self.app.thumb_scroll = ttk.Scrollbar(self.app.thumb_bar_frame, orient=tk.HORIZONTAL)
        self.app.thumb_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.app.thumb_canvas = tk.Canvas(
            self.app.thumb_bar_frame,
            height=80,
            bg='#2a2a2a',
            highlightthickness=0,
            xscrollcommand=self.app.thumb_scroll.set
        )
        self.app.thumb_scroll.config(command=self.app.thumb_canvas.xview)
        self.app.thumb_canvas.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        self.app.thumb_canvas.bind('<Configure>', lambda e: self.app.thumbnail.update_scrollregion())
        self.app.thumb_canvas.bind('<Button-1>', lambda e: self.app.thumbnail.on_click(e))

        self.app.canvas = tk.Canvas(image_frame, bg='#1a1a1a', highlightthickness=0)
        self.app.canvas.pack(fill=tk.BOTH, expand=True)
        self.app.canvas.bind('<Button-1>', self.app._on_main_canvas_click)

    def _setup_pixelation_settings(self):
        settings_frame = ttk.LabelFrame(self.app.control_frame, text="Pixelation", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(settings_frame, text="Block Size:").pack(anchor=tk.W)

        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=2)

        self.app.block_size_var = tk.StringVar(value="16")
        self.app.block_size_var.trace_add('write', lambda *args: self.app.slider._draw_slider())

        self.app.slider = BlockSizeSlider(settings_frame, size_frame, self.app.block_size_var)

    def _build_roi_settings(self):
        roi_frame = ttk.LabelFrame(self.app.control_frame, text="Region Selection", padding=5)
        roi_frame.pack(fill=tk.X, pady=(0, 10))

        self.app.roi_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            roi_frame, text="Enable ROI mode",
            variable=self.app.roi_mode_var, command=self.app._toggle_roi_mode
        ).pack(anchor=tk.W, pady=2)

        self.app.roi_info_label = ttk.Label(
            roi_frame, text="Click on image to select region",
            foreground='gray'
        )
        self.app.roi_info_label.pack(anchor=tk.W, pady=2)

        self.app.persistent_roi_var = tk.BooleanVar(value=False)
        self.app.persistent_roi_var.trace_add('write', self.app._on_persistent_roi_change)
        ttk.Checkbutton(
            roi_frame, text="Persistent ROI",
            variable=self.app.persistent_roi_var
        ).pack(anchor=tk.W, pady=2)
        ttk.Label(
            roi_frame, text="ROI mode stays enabled after Reset and when switching images",
            foreground='gray', font=('', 8)
        ).pack(anchor=tk.W, pady=(0, 5))

    def _setup_action_buttons(self):
        action_frame = ttk.Frame(self.app.control_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(action_frame, text="Apply Pixelation",
                   command=self.app.pixelation.apply, style="Accent.TButton").pack(
            fill=tk.X, pady=5)

    def _setup_status_bar(self):
        self.app.status_frame = ttk.Frame(self.app.root)
        self.app.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.app.status_label = ttk.Label(self.app.status_frame, text="No image loaded - Open an image to begin")
        self.app.status_label.pack(side=tk.LEFT, padx=10)

        self.app.progress_frame = ttk.Frame(self.app.status_frame, width=150)
        self.app.progress_frame.pack(side=tk.RIGHT, padx=10)
        self.app.progress_frame.pack_forget()
        self.app.progress_frame.pack_propagate(False)
        self.app.progress = ttk.Progressbar(self.app.progress_frame, mode='indeterminate')
        self.app.progress.pack(fill=tk.X, padx=2, pady=2)
