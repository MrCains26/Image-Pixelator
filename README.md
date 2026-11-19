# Image Pixelator 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\
A fast, cross-platform desktop application for pixelating images with full-image and Region-of-Interest (ROI) support.

## Features

- **Full-Image Pixelation** - Apply block-based pixelation to an entire image at once
- **ROI (Region of Interest) Mode** - Click and drag to select specific areas for pixelation while leaving the rest untouched
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
| Packaging    | PyInstaller (produces standalone `.exe` in onedir mode) |
| CI/CD        | GitHub Actions (cross-platform builds)       |

## Requirements

- Python 3.14+
- [requirements.txt](requirements.txt)

## Installation

### Pre-compiled (Recommended)

1. Download `Image-Pixelator.exe` and `Image-Pixelator.pkg` from the latest [release](https://github.com/yourusername/image-censor-pixel/releases)
2. Place both files in the same directory
3. Double-click `Image-Pixelator.exe`

***

### From Source

Install: `Python 3.14+`\
Clone the repo
<br>

**Install dependencies:**
```bash
pip install -r requirements.txt
pip install pyinstaller
```
Run:
`pyinstaller Image-Pixelator.spec --clean`\
Launch from: `dist/Image-Pixelator.exe`

>The compiled binary is placed in `dist/` as `Image-Pixelator.exe` and `Image-Pixelator.pkg`. The `.exe` references the `.pkg` at runtime for faster loading speed compared to a standalone `.exe` file.

***

### GitHub Actions

A CI workflow (`.github/workflows/build.yml`) automatically builds for Windows, macOS, and Linux on every stable push and PR. Artifacts are released on tagged commits.
