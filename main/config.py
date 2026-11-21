import json
import os


class ConfigManager:

    def __init__(self, config_file):
        self.config_file = config_file
        self.default_filename = "censored-image"
        self.show_save_popup = True
        self.keep_original_filenames = False
        self.custom_save_path = None

    def load(self):
        if not os.path.exists(self.config_file):
            return
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            self.default_filename = config.get("default_filename", "censored-image")
            self.show_save_popup = config.get("show_save_popup", True)
            self.keep_original_filenames = config.get("keep_original_filenames", False)
            save_path = config.get("custom_save_path")
            if save_path and save_path != "Use save dialog (default)":
                self.custom_save_path = save_path
        except (json.JSONDecodeError, KeyError):
            pass

    def save(self, app_ref):
        config = {
            "default_filename": app_ref.default_filename,
            "show_save_popup": app_ref.show_save_popup.get(),
            "keep_original_filenames": app_ref.keep_original_filenames.get(),
            "custom_save_path": app_ref.custom_save_path if app_ref.custom_save_path else "Use save dialog (default)"
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def apply_to_app(self, app_ref):
        app_ref.default_filename = self.default_filename
        app_ref.show_save_popup.set(self.show_save_popup)
        app_ref.keep_original_filenames.set(self.keep_original_filenames)
        app_ref.custom_save_path = self.custom_save_path
