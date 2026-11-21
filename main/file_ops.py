import os
from tkinter import filedialog, messagebox

from PIL import Image


class FileOperations:

    def __init__(self, app_ref):
        self.app = app_ref

    def open_image(self):
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
            idx = len(self.app.images)
            self.app.images.append(img)
            self.app.image_paths.append(filepath)
            self.app.image_states[idx] = {'original': img.copy(), 'processed': None, 'roi': []}
            self.app.selected_index = idx
            self.app._load_selected_image()
            self.app._update_thumbnail_bar()
            self.app._update_status()
            self.app._update_button_states()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")

    def open_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")

        if not folder:
            return

        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
        image_files = []

        for f in sorted(os.listdir(folder)):
            ext = os.path.splitext(f)[1].lower()
            if ext in image_extensions:
                image_files.append(os.path.join(folder, f))

        if not image_files:
            messagebox.showinfo("No Images", "No image files found in the selected folder.")
            return

        try:
            for idx, filepath in enumerate(image_files):
                img = Image.open(filepath)
                self.app.images.append(img)
                self.app.image_paths.append(filepath)
                self.app.image_states[idx] = {'original': img.copy(), 'processed': None, 'roi': []}

            self.app.selected_index = 0
            self.app._load_selected_image()
            self.app._update_thumbnail_bar()
            self.app._update_status()
            self.app._update_button_states()

            self.app.status_label.config(
                text=f"Loaded {len(self.app.images)} images from folder"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images from folder:\n{str(e)}")

    def save_image(self):
        if not self.app.current_image:
            messagebox.showwarning("Warning", "No image to save.")
            return

        image_to_save = self.app.current_image

        if self.app.image_paths and self.app.selected_index < len(self.app.image_paths):
            input_ext = os.path.splitext(self.app.image_paths[self.app.selected_index])[1].lower()
            original_name = os.path.splitext(os.path.basename(self.app.image_paths[self.app.selected_index]))[0]
        else:
            input_ext = ".png"
            original_name = self.app.default_filename

        format_map = {
            ".png": [("PNG files", "*.png")],
            ".jpg": [("JPEG files", "*.jpg *.jpeg")],
            ".jpeg": [("JPEG files", "*.jpg *.jpeg")],
            ".bmp": [("BMP files", "*.bmp")],
            ".gif": [("GIF files", "*.gif")],
            ".tiff": [("TIFF files", "*.tiff *.tif")],
            ".webp": [("WebP files", "*.webp")],
        }

        filetypes = format_map.get(input_ext, [("PNG files", "*.png")])

        if self.app.keep_original_filenames.get():
            default_name = f"{original_name}{input_ext}"
        else:
            default_name = f"{self.app.default_filename}{input_ext}"

        filepath = None

        if self.app.custom_save_path:
            if isinstance(self.app.custom_save_path, tuple):
                folder, filename = self.app.custom_save_path
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
                    filename += input_ext
                filepath = os.path.join(folder, filename)
            else:
                folder = self.app.custom_save_path
                filepath = os.path.join(folder, default_name)
        else:
            filepath = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=input_ext,
                initialfile=default_name,
                filetypes=filetypes
            )

        if not filepath:
            return

        try:
            if filepath.lower().endswith(('.jpg', '.jpeg')):
                image_to_save = image_to_save.convert('RGB')

            image_to_save.save(filepath)

            if self.app.show_save_popup.get():
                messagebox.showinfo("Success", f"Image saved to:\n{filepath}")
            else:
                self.app.status_label.config(text=f"Saved: {filepath}")

        except Exception as e:
            if self.app.show_save_popup.get():
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
            else:
                self.app.status_label.config(text=f"Save failed: {str(e)}")

    def download_all(self):
        if not self.app.image_states:
            messagebox.showwarning("Warning", "No images to download.")
            return

        download_dir = None
        if self.app.custom_save_path and isinstance(self.app.custom_save_path, str):
            download_dir = self.app.custom_save_path
        else:
            download_dir = filedialog.askdirectory(title="Choose Download Folder")

        if not download_dir:
            return

        saved_count = 0
        errors = []
        used_names = set()

        for idx, img_state in self.app.image_states.items():
            if not img_state['processed']:
                continue

            result = img_state['processed']
            ext = os.path.splitext(self.app.image_paths[idx])[1].lower()
            if self.app.keep_original_filenames.get():
                base_name = os.path.splitext(os.path.basename(self.app.image_paths[idx]))[0]
            else:
                base_name = self.app.default_filename
            counter = 1
            while True:
                if counter == 1:
                    candidate = f"{base_name}_{counter}{ext}"
                else:
                    candidate = f"{base_name}_{counter}{ext}"
                if candidate not in used_names:
                    break
                counter += 1
            filename = candidate
            used_names.add(filename)

            filepath = os.path.join(download_dir, filename)

            try:
                if filepath.lower().endswith(('.jpg', '.jpeg')):
                    result = result.convert('RGB')
                result.save(filepath)
                saved_count += 1
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")

        if saved_count > 0:
            msg = f"Saved {saved_count} image(s) to:\n{download_dir}"
            if errors:
                msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors)
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showinfo("No Images", "No pixelated images to save.\nApply pixelation to at least one image first.")

    def reset_image(self):
        if not self.app.image_states or not self.app.image_states.get(self.app.selected_index):
            return

        img_state = self.app.image_states[self.app.selected_index]

        self.app.canvas.delete('roi_selection')
        self.app.canvas.unbind('<ButtonPress-1>')
        self.app.canvas.unbind('<B1-Motion>')
        self.app.canvas.unbind('<ButtonRelease-1>')

        img_state['processed'] = None
        self.app.current_image = img_state['original'].copy()

        if self.app.persistent_roi_var.get():
            img_state['roi'] = []
        self.app.selection_tool = None

        if self.app.persistent_roi_var.get():
            self.app._create_selection_tool()
            self.app.roi_info_label.config(text="Click and drag on image to select region", foreground='black')
            self.app.status_label.config(text="Image reset - ROI mode enabled")
        else:
            self.app.roi_mode_var.set(False)
            self.app.roi_info_label.config(text="Click and drag on image to select region", foreground='gray')
            self.app.status_label.config(text="Image reset to original")

        self.app._display_image(self.app.current_image)

    def reset_all_images(self):
        if not self.app.image_states:
            return

        if self.app.reset_all_suppress and self.app.reset_all_suppress.get():
            self._do_reset_all_images()
            return

        self._confirm_dialog("Reset all edits will clear all pixelation and ROI selections for every loaded image. Continue?", self._do_reset_all_images)

    def _do_reset_all_images(self):
        for idx in self.app.image_states:
            img_state = self.app.image_states[idx]
            img_state['processed'] = None
            img_state['roi'] = []

        self.app.selected_index = 0
        self.app.current_image = None
        self.app.selection_tool = None
        self.app.roi_mode_var.set(False)
        self.app.persistent_roi_var.set(False)

        self.app.canvas.delete('all')
        self.app.canvas.delete('roi_selection')
        self.app.canvas.unbind('<ButtonPress-1>')
        self.app.canvas.unbind('<B1-Motion>')
        self.app.canvas.unbind('<ButtonRelease-1>')

        self.app._update_status()
        if self.app.images:
            self.app._load_selected_image()
        self.app.status_label.config(text="All edits reset")
        self.app._update_button_states()

    def clear_all(self):
        self.app.images = []
        self.app.image_paths = []
        self.app.selected_index = 0
        self.app.image_states = {}
        self.app.current_image = None
        self.app.selection_tool = None
        self.app.thumbnail_vars = []
        self.app.thumb_items = []

        self.app.roi_mode_var.set(False)
        self.app.persistent_roi_var.set(False)

        self.app.thumb_canvas.delete('all')
        self.app.canvas.delete('all')
        self.app._update_status()
        self.app.status_label.config(text="All images cleared")
        self.app._update_button_states()

    def _remove_thumbnail(self, index):
        if not self.app.images or index >= len(self.app.images):
            return

        if index == self.app.selected_index:
            if len(self.app.images) > 1:
                next_idx = min(index + 1, len(self.app.images) - 1)
                self.app.selected_index = next_idx
            else:
                self.app.selected_index = 0

        self.app.images.pop(index)
        self.app.image_paths.pop(index)
        self.app.image_states.pop(index, None)

        new_states = {}
        for new_idx, (orig_idx, state) in enumerate(sorted(self.app.image_states.items())):
            new_states[new_idx] = state
        self.app.image_states = new_states

        self.app._update_thumbnail_bar()
        if self.app.images:
            self.app._load_selected_image()
        else:
            self.app.current_image = None
            self.app.canvas.delete('all')
            self.app.roi_mode_var.set(False)
            self.app.persistent_roi_var.set(False)
            self.app.selection_tool = None
            self.app.roi_info_label.config(text="No image loaded", foreground='gray')
        self.app._update_status()
        self.app._update_button_states()
        self.app.status_label.config(text=f"Removed image #{index + 1}")

    def _confirm_dialog(self, message, on_yes):
        import tkinter as tk
        from tkinter import ttk

        dialog = tk.Toplevel(self.app.root)
        dialog.title("Confirm Action")
        dialog.geometry("400x220")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()

        if hasattr(self.app, '_window_icon') and self.app._window_icon is not None:
            dialog.iconphoto(True, self.app._window_icon)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 220) // 2
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(main_frame, text=message, wraplength=350, justify=tk.CENTER)
        lbl.pack(pady=(0, 10))

        reset_all_suppress_var = tk.BooleanVar()
        suppress_chk = ttk.Checkbutton(main_frame, text="Don't ask me again", variable=reset_all_suppress_var)
        suppress_chk.pack(pady=(0, 15))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()

        def on_yes_click():
            self.app.reset_all_suppress.set(reset_all_suppress_var.get())
            dialog.destroy()
            on_yes()

        ttk.Button(btn_frame, text="Yes", command=on_yes_click).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="No", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        dialog.focus_set()
        self.app.root.wait_window(dialog)
