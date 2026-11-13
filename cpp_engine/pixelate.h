// pixelate.h - C++ Image Pixelation Engine
// Fast pixelation using raw pixel manipulation
// Compile with: g++ -shared -O2 -o pixelate.dll pixelate.cpp

#ifndef PIXELATE_H
#define PIXELATE_H

#ifdef __cplusplus
extern "C" {
#endif

// Load image from file (returns pointer to pixel data, width, height)
// Returns NULL on failure
typedef struct {
    unsigned char* pixels;
    int width;
    int height;
    int channels; // 3 = RGB, 4 = RGBA
} ImageData;

// Apply pixelation to full image
// blockSize: size of each pixel block (2-50)
void pixelateFull(ImageData* img, int blockSize);

// Apply pixelation to ROI (region of interest)
// x, y: top-left corner of ROI
// w, h: width and height of ROI
// blockSize: size of each pixel block
void pixelateROI(ImageData* img, int x, int y, int w, int h, int blockSize);

// Save image to file (supports PNG and JPG)
int saveImage(const ImageData* img, const char* filename);

// Free image data
void freeImage(ImageData* img);

// Get error message (NULL if no error)
const char* getLastError();

#ifdef __cplusplus
}
#endif

#endif // PIXELATE_H
