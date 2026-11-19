"""
Settings dialog and configuration management UI.
"""

import os

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class SettingsDialog:

    def __init__(self, app_ref):
        self.app = app_ref
        self.settings_dropdown = None

    def toggle(self):
        if self.settings_dropdown is not None and self.settings_dropdown.winfo_exists():
            self.close()
        else:
            self.open()

    def open(self):
        if self.settings_dropdown is not None and self.settings_dropdown.winfo_exists():
            self.close()

        self.settings_dropdown = tk.Toplevel(self.app.root)
        self.settings_dropdown.transient(self.app.root)
        self.settings_dropdown.wm_geometry(f'+10+10')
        self.settings_dropdown.wm_deiconify()
        self.settings_dropdown.attributes('-topmost', True)
        self.settings_dropdown.protocol("WM_DELETE_WINDOW", self.close)

        inner = ttk.Frame(self.settings_dropdown, padding=10)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Default save name:", style="Menu.TLabel").pack(anchor=tk.W, pady=(0, 2))

        name_frame = ttk.Frame(inner)
        name_frame.pack(fill=tk.X, pady=(0, 10))

        self.save_name_var = tk.StringVar(value=self.app.default_filename)
        self.save_name_entry = ttk.Entry(name_frame, textvariable=self.save_name_var, width=30)
        self.save_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.save_name_entry.bind('<Control-BackSpace>', self._ctrl_backspace_name)

        ttk.Button(name_frame, text="Reset", command=self._reset_save_name).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Checkbutton(
            inner,
            text="Keep Original Filenames",
            variable=self.app.keep_original_filenames,
            command=lambda: self.app.config.save(self.app)
        ).pack(anchor=tk.W, pady=(2, 2))

        ttk.Checkbutton(
            inner,
            text="Show save location popup",
            variable=self.app.show_save_popup,
            command=lambda: self.app.config.save(self.app)
        ).pack(anchor=tk.W, pady=(2, 2))

        path_frame = ttk.Frame(inner)
        path_frame.pack(fill=tk.X, pady=(2, 2))

        ttk.Label(path_frame, text="Auto-save location:", style="Menu.TLabel").pack(anchor=tk.W)

        path_btn_frame = ttk.Frame(path_frame)
        path_btn_frame.pack(fill=tk.X, pady=2)

        self.path_var = tk.StringVar(value=self.app.custom_save_path if self.app.custom_save_path else "Use save dialog (default)")
        self.path_entry = ttk.Entry(
            path_btn_frame,
            textvariable=self.path_var,
            width=35
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.path_entry.bind('<Return>', lambda e: self._validate_manual_path())
        self.path_entry.bind('<FocusOut>', lambda e: self._validate_manual_path())
        self.path_entry.bind('<Control-BackSpace>', self._ctrl_backspace_path)

        ttk.Button(
            path_btn_frame,
            text="Choose folder",
            command=self._choose_save_folder
        ).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Button(
            path_btn_frame,
            text="Reset",
            command=self._reset_save_path
        ).pack(side=tk.LEFT)

        self.save_name_entry.bind('<Return>', lambda e: self._apply_save_name())
        self.save_name_entry.bind('<Escape>', lambda e: self.close())

        self.app.root.after(50, self._position)

    def _position(self):
        if self.settings_dropdown is None:
            return
        bx = self.app.settings_btn.winfo_rootx()
        by = self.app.settings_btn.winfo_rooty() + self.app.settings_btn.winfo_height()
        self.settings_dropdown.wm_geometry(f'+{bx}+{by}')

    def close(self):
        if self.settings_dropdown is not None and self.settings_dropdown.winfo_exists():
            if hasattr(self, 'save_name_var') and self.save_name_var.get().strip():
                self.app.default_filename = self.save_name_var.get().strip()

            if hasattr(self, 'path_var'):
                path = self.path_var.get().strip()
                if path and path != "Use save dialog (default)":
                    if os.path.exists(path):
                        self.app.custom_save_path = path
                    elif path.lower().startswith(('http://', 'https://')):
                        pass
                    else:
                        self.app.custom_save_path = path

            self.app.config.save(self.app)
            self.settings_dropdown.destroy()
        self.settings_dropdown = None

    def _apply_save_name(self):
        val = self.save_name_var.get().strip()
        if val:
            self.app.default_filename = val
        self.app.config.save(self.app)

    def _reset_save_name(self):
        self.app.default_filename = "censored-image"
        self.save_name_var.set("censored-image")
        self.app.config.save(self.app)

    def _ctrl_backspace_name(self, event):
        text = self.save_name_var.get()
        idx = self.save_name_entry.index(tk.INSERT)
        if idx <= 0:
            return "break"

        delimiters = {' ', '_', '-'}

        pos = idx - 1
        while pos >= 0 and text[pos] not in delimiters:
            pos -= 1

        if pos >= 0:
            if text[pos] == text[idx - 1]:
                self.save_name_var.set(text[:pos] + text[idx:])
            else:
                self.save_name_var.set(text[:pos + 1] + text[idx:])
        else:
            self.save_name_var.set(text[idx:])
        return "break"

    def _ctrl_backspace_path(self, event):
        text = self.path_var.get()
        idx = self.path_entry.index(tk.INSERT)
        if idx <= 0:
            return "break"

        delimiters = {' ', '/', '\\', '_', '-'}

        pos = idx - 1
        while pos >= 0 and text[pos] not in delimiters:
            pos -= 1

        if pos >= 0:
            if text[pos] == text[idx - 1]:
                self.path_var.set(text[:pos] + text[idx:])
            else:
                self.path_var.set(text[:pos + 1] + text[idx:])
        else:
            self.path_var.set(text[idx:])
        return "break"

    def _show_file_dialog(self):
        x = self.app.settings_btn.winfo_rootx()
        y = self.app.settings_btn.winfo_rooty() + self.app.settings_btn.winfo_height()

        self.settings_dropdown.attributes('-topmost', False)

        parent_win = tk.Toplevel(self.app.root)
        parent_win.withdraw()
        parent_win.attributes('-topmost', True)
        parent_win.geometry(f'+{x}+{y}')
        parent_win.deiconify()
        parent_win.attributes('-topmost', False)

        filepath = filedialog.askdirectory(
            parent=parent_win,
            title="Choose auto-save folder"
        )

        parent_win.destroy()

        if self.settings_dropdown and self.settings_dropdown.winfo_exists():
            self.settings_dropdown.attributes('-topmost', True)
            self.settings_dropdown.grab_set()

        return filepath

    def _choose_save_folder(self):
        folder = self._show_file_dialog()
        if folder:
            self.app.custom_save_path = folder
            self.path_var.set(folder)
            self.app.config.save(self.app)

    def _reset_save_path(self):
        self.app.custom_save_path = None
        self.path_var.set("Use save dialog (default)")
        self.app.config.save(self.app)

    def _validate_manual_path(self):
        path = self.path_var.get().strip()
        if not path or path == "Use save dialog (default)":
            self.app.custom_save_path = None
            self.app.config.save(self.app)
            return

        if not os.path.exists(path):
            dialog = tk.Toplevel(self.app.root)
            dialog.wm_title("Folder Does Not Exist")
            dialog.wm_geometry("+{}+{}".format(
                self.app.root.winfo_rootx() + (self.app.root.winfo_width() - 400) // 2,
                self.app.root.winfo_rooty() + (self.app.root.winfo_height() - 200) // 2
            ))
            dialog.attributes('-topmost', True)
            dialog.transient(self.app.root)
            dialog.grab_set()

            info_frame = ttk.Frame(dialog, padding=15)
            info_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(
                info_frame,
                text=f'"{path}" does not exist.\n\nContinuing with this directory will create a new folder.\nThe images will be downloaded to that folder.',
                wraplength=380,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, 10))

            btn_frame = ttk.Frame(info_frame)
            btn_frame.pack(fill=tk.X)

            result = {'choice': None}

            def on_yes():
                result['choice'] = 'yes'
                dialog.destroy()

            def on_no():
                result['choice'] = 'no'
                dialog.destroy()

            def on_choose():
                dialog.destroy()
                folder = self._show_file_dialog()
                if folder:
                    self.app.custom_save_path = folder
                    self.path_var.set(folder)
                    self.app.config.save(self.app)

            ttk.Button(btn_frame, text="OK", command=on_yes).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(btn_frame, text="No", command=on_no).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(btn_frame, text="Choose Folder", command=on_choose).pack(side=tk.LEFT)

            self.app.root.wait_window(dialog)

            if result['choice'] == 'yes':
                try:
                    os.makedirs(path, exist_ok=True)
                    self.app.custom_save_path = path
                    self.path_var.set(path)
                    self.app.config.save(self.app)
                    messagebox.showinfo("Success", f"Folder created:\n{path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create folder:\n{str(e)}")
            else:
                self.path_var.set("Use save dialog (default)")
        else:
            self.app.custom_save_path = path
            self.path_var.set(path)
            self.app.config.save(self.app)
