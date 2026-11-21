# Image Pixelator 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Build Status](https://img.shields.io/github/actions/workflow/status/MrCains26/Image-Pixelator/build.yml?label=Build)
[![GitHub Release](https://img.shields.io/github/v/release/MrCains26/Image-Pixelator)](https://github.com/MrCains26/Image-Pixelator/releases)
[![Python](https://img.shields.io/badge/Python-3.14%2B-blue)](https://www.python.org/)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-222)](https://github.com/MrCains26/Image-Pixelator/releases)\
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
| Image Engine | Python + Pillow (PIL) — optimized and resize |
| Packaging    | PyInstaller (produces executable) |
| CI/CD        | GitHub Actions (cross-platform builds)       |

## Requirements

- Python 3.14+
- [requirements.txt](requirements.txt)
   - Pillow
   - tkinterdnd2
   - pystray

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

1. Download the .zip file for your operating system (Windows, macOS, or Linux) from the latest [release](https://github.com/MrCains26/Image-Pixelator/releases)
2. Extract the contents to a folder of your choice
3. Double-click Image-Pixelator.exe (Windows) or the executable file (macOS/Linux)

>The compiled executable folder contains `Image-Pixelator.exe` (or Linux/MacOS equivalent) and `_internal`. The `.exe` references the `_internal` at runtime for faster loading speed compared to a standalone `.exe` file, make sure they are always in the same folder/directory.

***

## Building from Source

Follow these steps to compile the application from the source code on your local machine.

### Prerequisites
- **Python 3.14+** installed on your computer.
- **Git** (to clone the repository).

### 1. Setup (All Operating Systems)
1.  Clone the repository or download the source files to your computer.
2.  Open your **Terminal** or **Command Prompt** in the repository directory.
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```

### 2. Build the Executable

Run the following command to compile the Python code into a standalone application:

```bash
pyinstaller Image-Pixelator.spec --clean
```

This process will generate a new folder named dist/ in your repository.

### 3. Run the Application

**Windows**
1. Open the `dist/` folder.
2. Double-click `Image-Pixelator.exe` to launch the program.

**macOS**
1. Open the `dist/` folder.
2. Double-click `Image-Pixelator.app`.

**Linux**
1. Open your terminal and navigate to the `dist/` folder.
2. Make the application executable:
   
```bash
chmod +x Image-Pixelator
```

3. Launch the program:
`./Image-Pixelator`
>[!NOTE]
>If you encounter a library error on Linux, you may need to install Tkinter system dependencies (e.g., `sudo apt-get install python3-tk libx11-xcb1` on Ubuntu/Debian).

>[!WARNING]
>you may get a popup saying "Windows protected your PC" or a warning stating that Apple cannot verify the app.
>
>**Windows**
>1. Click **More info** (or **Details**) on the blue warning bar.
>2. Click the **Run anyway** button.
>   
>**macOS**
>1. Right-click (or Control-click) the `Image-Pixelator.app` file.
>2. Select **Open** from the context menu.
>3. Click **Open** again in the dialog box that appears.
>   
>These warnings appear because **Image Pixelator** is a free, open-source application without a paid digital signature. This is a standard warning for any new, unsigned software. You can verify the safety of the code by browsing the source files on this repository.
