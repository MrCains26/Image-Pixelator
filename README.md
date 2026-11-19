# Image Pixelator 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\
A fast, resource efficient, cross-platform desktop application for pixelating images with full-image and Region-of-Interest (ROI) support.

## Features

- **Full-Image Pixelation** - Apply block-based pixelation to an entire image at once
- **ROI (Region of Interest) Mode** - Select specific areas for pixelation while leaving the rest untouched
- **Persistent ROI** - ROI mode can be enabled to stay active across reset operations and image switches
- **Batch Processing** - Open and process multiple images at once from a single folder or via drag-and-drop
- **Custom Block Sizes** - Adjustable via slider or direct input (range: 2-64 pixels) + preset buttons (Subtle, Medium, Strong, Extreme)
- **Thumbnail Bar** - Visual overview of all loaded images, switch between images.
- **Cross-Platform** - Builds and runs on Windows, macOS, and Linux

## Built With

| Layer        | Technology                                  |
|--------------|---------------------------------------------|
| GUI          | Python + Tkinter + tkinterdnd2              |
| Image Engine | Python + Pillow (PIL) — optimized resize technique |
| Packaging    | PyInstaller (produces executable) |
| CI/CD        | GitHub Actions (cross-platform builds)       |

## Requirements

- Python 3.14+
- [requirements.txt](requirements.txt)
   - Pillow
   - tkinterdnd2

## Supported Formats
PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP

## Usage
Open an image, adjust the block size slider, and click **Apply Pixelation**. Click and drag on the image to select regions for **ROI** mode.
<br><br>
**Shortcuts:**\
`Ctrl+O` Open an image
<br>
`Ctrl+S` Save current image
<br>
`Ctrl+R` Reset edits on current image
<br>
`Ctrl+P` Apply Pixelation to current image

## Installation

### Pre-compiled (Recommended)

1. Download `Image-Pixelator.exe` and `Image-Pixelator.pkg` from the latest [release](https://github.com/yourusername/image-censor-pixel/releases)
2. Place both files in the same directory
3. Double-click `Image-Pixelator.exe`

***

### From Source

1. Install Python 3.14+
2. Clone the repository
3. Open your terminal or CLI in the cloned directory
<br>

**Install dependencies:**
```bash
pip install -r requirements.txt
pip install pyinstaller
```
Build: `pyinstaller Image-Pixelator.spec --clean`\
Launch from: `dist/Image-Pixelator.exe`

>The compiled executable is placed in `dist/` as `Image-Pixelator.exe` and `Image-Pixelator.pkg`. The `.exe` references the `.pkg` at runtime for faster loading speed compared to a standalone `.exe` file, make sure they are in the same folder.
