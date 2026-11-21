import threading

import tkinter as tk


class PixelationHandler:

    def __init__(self, app_ref):
        self.app = app_ref

    def apply(self):
        if not self.app.images:
            tk.messagebox.showwarning("Warning", "Please open an image first.")
            return

        if self.app.selected_index not in self.app.image_states:
            tk.messagebox.showwarning("Warning", "Please open an image first.")
            return

        try:
            block_size = int(self.app.block_size_var.get())
        except (ValueError, tk.TclError):
            block_size = 16
            self.app.block_size_var.set("16")

        if block_size < 2:
            tk.messagebox.showerror("Error", "Block size must be at least 2.")
            return

        self.app.progress_frame.pack(side=tk.RIGHT, padx=10)
        self.app.progress.start()
        self.app.status_label.config(text="Processing...")

        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        try:
            img_state = self.app.image_states[self.app.selected_index]
            source = img_state['original'].copy()
            if source.mode != 'RGB':
                source = source.convert('RGB')

            if self.app.roi_mode_var.get() and img_state.get('roi', []):
                result = source.copy()
                pixels = result.load()
                end_x = result.width
                end_y = result.height
                for (rx, ry, rw, rh) in img_state['roi']:
                    region_end_x = min(rx + rw, end_x)
                    region_end_y = min(ry + rh, end_y)

                    for by in range(ry, region_end_y, int(self.app.block_size_var.get())):
                        for bx in range(rx, region_end_x, int(self.app.block_size_var.get())):
                            block_end_x = min(bx + int(self.app.block_size_var.get()), region_end_x)
                            block_end_y = min(by + int(self.app.block_size_var.get()), region_end_y)
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
            else:
                result = self.app.engine.pixelate(source, int(self.app.block_size_var.get()))

            img_state['processed'] = result.copy()
            self.app.current_image = result
            self.app.root.after(0, self._after_processing)

        except Exception as err:
            import traceback
            traceback.print_exc()
            self.app.root.after(0, lambda e=err: self._processing_error(str(e)))

    def _after_processing(self):
        self.app.progress.stop()
        self.app.progress_frame.pack_forget()
        self.app._display_image(self.app.current_image)
        self.app.status_label.config(text="Pixelation applied successfully")

    def _processing_error(self, error):
        self.app.progress.stop()
        self.app.progress_frame.pack_forget()
        tk.messagebox.showerror("Error", f"Processing failed:\n{error}")
        self.app.status_label.config(text="Processing failed")
