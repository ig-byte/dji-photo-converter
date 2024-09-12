# DJI Photo Converter
A color palette converter for thermal images that allows adding telemetry information directly to the processed images.

## Description
This project processes thermal images captured by DJI drones, converting the color palette and adding telemetry data such as date, GPS coordinates, and altitude. The script uses the DJI SDK to process the images and applies visual modifications to the final output.

## Workflow
1. **Thermal image processing**: The script takes images from the `img` folder, changes the color palette according to the available options (such as "iron_red" or "white_hot"), and generates new images with the processed data.
2. **Add telemetry**: If the images contain telemetry metadata, this data is extracted and added to the output image as overlay text. The data includes date, time, GPS coordinates, and altitude.
3. **Save processed images**: The images with the new palette and telemetry are saved in the `img_new` folder with the same name as the original images.

## Folder Structure

```
dji-photo-converter/
├── img/               # Images to convert (Required)
├── temp/              # Stores .raw temporary files for conversion to jpg (Created after script execution)
├── metadata/          # Stores .txt files with the names of images containing telemetry data (Created after script execution)
├── img_new/           # Processed images with new palette and telemetry (Created after script execution)
└── fuente/            # Contains custom font files for text in images (Created after script execution)
```


## Requirements
1. **Python 3.x**
2. **Pillow**: Library for image manipulation in Python.
3. **ExifTool**: Tool for reading and writing EXIF metadata in images.
4. **DJI SDK**: Used to process thermal images and change the color palette.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/dji-photo-converter.git

## Usage
1. Place the thermal images in the img folder.
2. Run the script to process the images:
  **python dji-photo-converter.py**
