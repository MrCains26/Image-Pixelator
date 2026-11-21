import os
import sys
import threading
from pathlib import Path

import tkinter as tk
from tkinter import ttk
import tkinterdnd2
from PIL import Image
import pystray

from engine import PixelateEngine
from selection import SelectionTool
from config import ConfigManager
from slider import BlockSizeSlider
from file_ops import FileOperations
from thumbnail import ThumbnailManager
from display import ImageDisplay
from pixelation import PixelationHandler
from settings import SettingsDialog
from dnd import DragDropHandler
from ui import UILayout


class PixelatorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Image Pixelator")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        if getattr(sys, 'frozen', False):
            app_data = os.path.join(os.environ.get('APPDATA'), 'Image-Pixelator')
        else:
            app_data = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(app_data, exist_ok=True)
        self.config_file = os.path.join(app_data, "settings.json")

        self.images = []
        self.image_paths = []
        self.selected_index = 0
        self.image_states = {}
        self.current_image = None
        self.selection_tool = None
        self.display_image = None
        self.tk_image = None
        self.image_w = 0
        self.image_h = 0
        self.thumbnail_vars = []
        self.thumb_items = []
        self.default_filename = "censored-image"
        self.show_save_popup = tk.BooleanVar(value=True)
        self.keep_original_filenames = tk.BooleanVar(value=False)
        self.custom_save_path = None
        self.reset_all_suppress = tk.BooleanVar(value=False)

        self.settings_dropdown = None
        self.menu_bar = None
        self._window_icon = None
        self.reset_frame = None
        self.status_frame = None
        self.close_x_ids = {}

        self._init_modules()
        self._load_config()
        self._setup_ui()
        self._setup_bindings()
        self._update_button_states()

    def _init_modules(self):
        self.engine = PixelateEngine()
        self.config = ConfigManager(self.config_file)
        self.file_ops = FileOperations(self)
        self.thumbnail = ThumbnailManager(self)
        self.display = ImageDisplay(self)
        self.pixelation = PixelationHandler(self)
        self.settings = SettingsDialog(self)
        self.dnd = DragDropHandler(self.root, self)
        self.ui = UILayout(self)

    def _load_config(self):
        self.config.load()
        self.config.apply_to_app(self)

    def _setup_ui(self):
        self.ui.setup()
        self.dnd.setup()

    def _setup_bindings(self):
        self.root.bind('<Control-o>', lambda e: self.file_ops.open_image())
        self.root.bind('<Control-s>', lambda e: self.file_ops.save_image())
        self.root.bind('<Control-r>', lambda e: self.file_ops.reset_image())
        self.root.bind('<Control-p>', lambda e: self.pixelation.apply())
        self.slider.entry.bind('<FocusOut>', lambda e: self.slider._validate_block_size())

    def _update_button_states(self):
        has_images = len(self.images) > 0
        self.download_this_btn.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.reset_btn.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.reset_all_btn.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.clear_all_btn.config(state=tk.NORMAL if has_images else tk.DISABLED)
        self.download_all_btn.config(state=tk.NORMAL if len(self.images) > 1 else tk.DISABLED)

    def _update_status(self):
        if self.images:
            img = self.images[self.selected_index]
            self.status_label.config(
                text=f"Image {self.selected_index + 1}/{len(self.images)} | {img.size[0]}x{img.size[1]} | {img.mode}"
            )
        else:
            self.status_label.config(text="No image loaded - Open an image to begin")

    def _load_selected_image(self):
        if not self.images or not self.image_states:
            return

        if self.selected_index not in self.image_states:
            self.image_states[self.selected_index] = {'original': self.images[self.selected_index].copy(), 'processed': None, 'roi': []}

        img_state = self.image_states[self.selected_index]
        self.current_image = img_state['processed'].copy() if img_state['processed'] else img_state['original'].copy()
        self.selection_tool = None
        self.roi_mode_var.set(False)
        self.canvas.delete('roi_selection')
        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        self.display.display(self.current_image)

        should_enable_roi = self.persistent_roi_var.get() or bool(img_state['roi'])
        if should_enable_roi:
            self.roi_mode_var.set(True)
            self.roi_info_label.config(text="Click and drag on image to select region", foreground='black')
            if self.persistent_roi_var.get():
                self.status_label.config(text="Persistent ROI enabled")
            else:
                self.status_label.config(text="ROI restored for this image")
            self.root.after(20, self._create_selection_tool)
            self.root.after(30, self._redraw_roi_selections)
        else:
            self.roi_info_label.config(text="ROI mode disabled - full image pixelation", foreground='gray')
            self.status_label.config(text="ROI mode disabled - full image pixelation")

    def _update_thumbnail_bar(self):
        self.thumbnail.update()

    def _update_thumb_scrollregion(self, event=None):
        self.thumbnail.update_scrollregion()

    def _on_main_canvas_click(self, event):
        if self.slider.entry.focus_displayof() == self.slider.entry:
            self.slider._validate_block_size()
            self.slider.entry.icursor(self.slider.entry.index(tk.END))
            self.slider.entry.selection_clear()
            self.settings_btn.focus()

    def _toggle_roi_mode(self):
        if self.roi_mode_var.get():
            if not self.images or self.selected_index >= len(self.images):
                self.roi_mode_var.set(False)
                self.roi_info_label.config(text="No image loaded", foreground='gray')
                return
            self.roi_info_label.config(text="Click and drag on image to select region", foreground='black')
            self.root.after(100, self._create_selection_tool)
        else:
            self.roi_info_label.config(text="ROI mode disabled - full image pixelation", foreground='gray')
            if self.selection_tool:
                self.selection_tool.clear_selection()
            self.selection_tool = None
            self.status_label.config(text="ROI mode disabled")

    def _on_persistent_roi_change(self, *args):
        if self.persistent_roi_var.get() and not self.roi_mode_var.get():
            if self.images and self.selected_index < len(self.images):
                self.roi_mode_var.set(True)
                self.roi_info_label.config(text="Click and drag on image to select region", foreground='black')
                self._create_selection_tool()
                self.status_label.config(text="Persistent ROI enabled - ROI mode activated")
            else:
                self.persistent_roi_var.set(False)
                self.status_label.config(text="Open an image first to enable persistent ROI")
        else:
            self.status_label.config(text="Persistent ROI disabled")

    def _create_selection_tool(self):
        try:
            if not self.image_states or not self.image_states.get(self.selected_index):
                return
            img_state = self.image_states[self.selected_index]
            if not img_state['original'] or self.image_w == 0 or self.image_h == 0:
                self.root.after(50, self._create_selection_tool)
                return

            self.canvas.unbind('<ButtonPress-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')

            self.selection_tool = SelectionTool(
                self.canvas,
                self.status_label,
                on_select=self._on_region_selected
            )
            self.selection_tool.set_app_ref(self)
            self.selection_tool.set_image(self.image_w, self.image_h)
            self._redraw_roi_selections()
        except Exception as e:
            import traceback
            self.status_label.config(text=f"ROI Error: {str(e)}")
            traceback.print_exc()

    def _on_region_selected(self, x, y, w, h):
        if not self.image_states:
            return
        img_state = self.image_states[self.selected_index]
        orig_img = img_state['original']

        scale_x = self.image_w / orig_img.width if orig_img.width > 0 else 1
        scale_y = self.image_h / orig_img.height if orig_img.height > 0 else 1

        orig_x = int(x / scale_x)
        orig_y = int(y / scale_y)
        orig_w = int(w / scale_x)
        orig_h = int(h / scale_y)

        orig_x = max(0, orig_x)
        orig_y = max(0, orig_y)
        orig_w = min(orig_w, orig_img.width - orig_x)
        orig_h = min(orig_h, orig_img.height - orig_y)

        self.image_states[self.selected_index]['roi'].append((orig_x, orig_y, orig_w, orig_h))
        self.status_label.config(
            text=f"Region {len(self.image_states[self.selected_index]['roi'])} selected: ({orig_x}, {orig_y}) {orig_w}x{orig_h} pixels"
        )
        self._redraw_roi_selections()

    def _redraw_roi_selections(self):
        self.canvas.delete('roi_selection')
        if not self.image_states:
            return
        img_state = self.image_states[self.selected_index]
        orig_img = img_state['original']

        if self.image_w == 0 or self.image_h == 0 or orig_img.width == 0 or orig_img.height == 0:
            self.root.after(50, self._redraw_roi_selections)
            return

        scale_x = self.image_w / orig_img.width if orig_img.width > 0 else 1
        scale_y = self.image_h / orig_img.height if orig_img.height > 0 else 1
        selections = self.image_states[self.selected_index]['roi']
        for sx, sy, sw, sh in selections:
            sx_d = int(sx * scale_x)
            sy_d = int(sy * scale_y)
            sw_d = int(sw * scale_x)
            sh_d = int(sh * scale_y)
            self.canvas.create_rectangle(
                sx_d, sy_d, sx_d + sw_d, sy_d + sh_d,
                outline='red', width=2, dash=(4, 4),
                tags='roi_selection'
            )

    def _display_image(self, image):
        self.display.display(image)


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        base = Path(sys.executable).parent
        if (base / relative_path).exists():
            return base / relative_path
        internal = base / "_internal"
        if (internal / relative_path).exists():
            return internal / relative_path
        return base / relative_path
    else:
        return Path(__file__).parent / ".." / relative_path


def main():
    root = tkinterdnd2.TkinterDnD.Tk()

    try:
        style = ttk.Style()
        style.theme_use('vista')
    except Exception:
        try:
            style = ttk.Style()
            style.theme_use('clam')
        except Exception:
            pass

    icon_png_path = resource_path(Path("assets") / "icon.png")
    app_icon = None
    if icon_png_path.exists():
        try:
            app_icon = tk.PhotoImage(file=str(icon_png_path))
            root.iconphoto(True, app_icon)
        except Exception:
            pass

    icon_ico_path = resource_path(Path("assets") / "icon.ico")
    if not app_icon and icon_ico_path.exists():
        root.iconbitmap(str(icon_ico_path))

    tray_image = None
    if icon_png_path.exists():
        try:
            tray_image = Image.open(str(icon_png_path)).convert("RGBA")
            tray_icon = pystray.Icon("Image Pixelator", tray_image, "Image Pixelator")
            tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
            tray_thread.start()
        except Exception:
            pass

    def on_close():
        try:
            tray_icon.stop()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    style.configure("Menu.TFrame", background='#f5f5f5')
    style.configure("Menu.TButton", background='#f5f5f5', foreground='#333333')
    style.configure("Menu.TLabel", background='#f0f0f0', foreground='#333333')

    app = PixelatorApp(root)
    app._window_icon = app_icon
    root.mainloop()


if __name__ == '__main__':
    main()
