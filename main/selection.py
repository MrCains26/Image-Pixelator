import tkinter as tk


class SelectionTool:

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
        self.app_ref = None

        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def set_app_ref(self, app_ref):
        self.app_ref = app_ref

    def _roi_enabled(self):
        if self.app_ref and hasattr(self.app_ref, 'roi_mode_var'):
            return self.app_ref.roi_mode_var.get()
        return False

    def set_image(self, image_width, image_height):
        self.image_width = image_width
        self.image_height = image_height

    def on_press(self, event):
        if not self._roi_enabled():
            return
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
        if not self._roi_enabled():
            return
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
            outline='red', width=2, dash=(4, 4),
            tags='roi_selection'
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

    def clear_selection(self):
        self.canvas.delete('roi_selection')
        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.start_x = None
        self.start_y = None
        self.is_selecting = False
        self.selection_rect = None
