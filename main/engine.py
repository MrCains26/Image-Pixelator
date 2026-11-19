"""
Image pixelation engine using PIL.
"""

from PIL import Image


class PixelateEngine:

    def __init__(self):
        pass

    def pixelate(self, image, block_size, x=0, y=0, w=None, h=None):
        if w is None:
            w = image.width
        if h is None:
            h = image.height

        if x == 0 and y == 0 and w == image.width and h == image.height:
            return self._pixelate_full(image, block_size)
        else:
            return self._pixelate_roi(image, block_size, x, y, w, h)

    def _pixelate_full(self, image, block_size):
        img = image.convert('RGB')
        if block_size <= 1:
            return img

        new_w = max(1, img.width // block_size)
        new_h = max(1, img.height // block_size)
        pixelated = img.resize((new_w, new_h), Image.NEAREST)
        pixelated = pixelated.resize((img.width, img.height), Image.NEAREST)
        return pixelated

    def _pixelate_roi(self, image, block_size, x, y, w, h):
        img = image.convert('RGB').copy()
        pixels = img.load()
        end_x = min(x + w, img.width)
        end_y = min(y + h, img.height)

        for by in range(y, end_y, block_size):
            for bx in range(x, end_x, block_size):
                block_end_x = min(bx + block_size, end_x)
                block_end_y = min(by + block_size, end_y)
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

        return img
