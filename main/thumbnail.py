from PIL import Image, ImageTk

import tkinter as tk


class ThumbnailManager:

    THUMB_W = 75
    THUMB_H = 55
    MARGIN = 5
    Y_OFFSET = 10

    def __init__(self, app_ref):
        self.app = app_ref

    def update(self):
        self.app.thumb_canvas.delete('all')
        self.app.thumbnail_vars = []
        self.app.thumb_items = []
        self.app.thumb_close_ids = []

        if not self.app.images:
            return

        start_x = self.MARGIN

        for idx, img in enumerate(self.app.images):
            bg_id = self.app.thumb_canvas.create_rectangle(
                start_x - 1, self.Y_OFFSET - 1, start_x + self.THUMB_W + 1,
                self.Y_OFFSET + self.THUMB_H + 1,
                fill='#1a1a1a', outline='',
                tags=(f'thumb_bg_{idx}', 'thumb'),
                state='hidden'
            )
            self.app.thumb_items.append(bg_id)

            thumb_img = img.copy()
            thumb_img.thumbnail((self.THUMB_W, self.THUMB_H), Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumb_img)
            self.app.thumbnail_vars.append(photo)

            item_id = self.app.thumb_canvas.create_image(
                start_x + self.THUMB_W // 2, self.Y_OFFSET + self.THUMB_H // 2,
                image=photo, anchor='center', tags=(f'thumb_{idx}', 'thumb')
            )
            self.app.thumb_items.append(item_id)

            num_text = self.app.thumb_canvas.create_text(
                start_x, self.Y_OFFSET,
                text=f"#{idx + 1}",
                anchor='nw',
                fill='#ffffff',
                font=('', 8),
                tags=(f'thumb_{idx}', 'thumb')
            )

            close_x = start_x + self.THUMB_W - 5
            close_y = self.Y_OFFSET + 3
            self.app.close_x_ids = getattr(self.app, 'close_x_ids', {})
            close_bg_id = self.app.thumb_canvas.create_rectangle(
                close_x - 6, close_y - 5, close_x + 4, close_y + 5,
                fill='#2a2a2a', outline='',
                tags=(f'close_bg_{idx}', f'close_{idx}'),
                state='normal'
            )
            close_x_id = self.app.thumb_canvas.create_text(
                close_x, close_y,
                text="\u2715",
                anchor='center',
                fill='#ffffff',
                font=('', 8, 'bold'),
                tags=(f'close_{idx}', 'close_button')
            )
            self.app.thumb_canvas.tag_bind(
                f'close_{idx}', '<Button-1>',
                lambda e, i=idx: self.app.file_ops._remove_thumbnail(i)
            )
            self.app.close_x_ids[idx] = close_bg_id
            self.app.close_x_ids[idx + 1000] = close_x_id

            self.app.thumb_canvas.tag_bind(
                f'thumb_{idx}', '<Enter>',
                lambda e, i=idx: self._on_hover_in(i)
            )
            self.app.thumb_canvas.tag_bind(
                f'thumb_{idx}', '<Leave>',
                lambda e, i=idx: self._on_hover_out(i)
            )

            start_x += self.THUMB_W + self.MARGIN

        self.app.thumb_canvas.config(scrollregion=self.app.thumb_canvas.bbox('all'))

    def on_click(self, event):
        x = event.x
        y = event.y

        start_x = self.MARGIN

        for idx in range(len(self.app.images)):
            item_x = start_x
            if item_x <= x < item_x + self.THUMB_W and self.Y_OFFSET <= y < self.Y_OFFSET + self.THUMB_H:
                self._select_image(idx)
                return
            start_x += self.THUMB_W + self.MARGIN

    def _on_hover_in(self, index):
        bg_tag = f'thumb_bg_{index}'
        self.app.thumb_canvas.itemconfig(bg_tag, state='normal', fill='#555555')
        if hasattr(self.app, 'close_x_ids'):
            bg_id = self.app.close_x_ids.get(index)
            if bg_id:
                self.app.thumb_canvas.itemconfig(bg_id, fill='#555555')

    def _on_hover_out(self, index):
        bg_tag = f'thumb_bg_{index}'
        self.app.thumb_canvas.itemconfig(bg_tag, state='hidden')
        if hasattr(self.app, 'close_x_ids'):
            bg_id = self.app.close_x_ids.get(index)
            if bg_id:
                self.app.thumb_canvas.itemconfig(bg_id, fill='#2a2a2a')

    def _select_image(self, index):
        if not self.app.images or index == self.app.selected_index:
            return
        self.app.selected_index = index
        self.app._load_selected_image()
        self.app._update_status()

    def update_scrollregion(self, event=None):
        self.app.thumb_canvas.config(scrollregion=self.app.thumb_canvas.bbox('all'))
