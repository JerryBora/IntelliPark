
# IntelliPark - Smart Parking Detection System 🚗🅿️

IntelliPark is an intelligent parking management system that uses computer vision and machine learning to detect available parking spaces in real-time from video feeds. The system can monitor parking lots through YouTube live streams, detect vehicles, and track parking space occupancy.

## Features

- **Real-time Parking Detection**: Uses YOLO object detection to identify vehicles in parking spaces
- **Multiple Configuration Support**: Supports different parking lot layouts through JSON configuration files
- **Live Status Dashboard**: Displays real-time metrics of available and occupied parking spaces
- **YouTube Stream Integration**: Connects to live YouTube streams for real-time monitoring
- **Interactive Configuration**: Visual tools for defining parking spaces

## Technology Stack

- **Computer Vision**: OpenCV for image processing
- **Machine Learning**: Ultralytics YOLO for object detection
- **Video Processing**: yt-dlp for YouTube video stream handling

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/IntelliPark.git
   cd IntelliPark
   ```

2. Install the required dependencies:
   ```
   pip install -r ml_service/requirements.txt
   ```

3. Download the YOLO model file (`yolo11s.pt`) and place it in the `ml_service` directory.

## Usage

1. Navigate to the ml_service directory:
   ```
   cd ml_service
   ```

2. Run the live processing script:
   ```
   python live2.py
   ```

3. Enter a YouTube URL of a parking lot live stream when prompted

4. Use the interactive interface to:
   - Press 'A' to add parking spaces (click to define 4 corners)
   - Press 'C' to clear the last defined parking space
   - Press 'Q' to quit the application

5. View real-time statistics on the video feed

## Parking Space Configuration

The system uses JSON files to define parking spaces. Each parking space is represented as a polygon with coordinates.

### Creating New Configurations

1. Use the interactive mode in live2.py to define parking spaces visually
2. Parking spaces are automatically saved to `parking_spaces2.json`
3. The configuration file can be edited manually if needed

Example configuration format:
```json
[
  [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
  [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
]
```

## System Components

### Live Processing Script (`live2.py`)

The core application that provides:
- Interactive parking space definition
- Real-time vehicle detection
- Occupancy monitoring
- Visual feedback

### Parking Space Management

- **Loading Configurations**: Loads parking space layouts from JSON files
- **Saving Configurations**: Saves modified parking space layouts
- **Processing Frames**: Analyzes video frames to detect vehicles and determine parking space occupancy

### Video Stream Processing

- **YouTube Integration**: Extracts video streams from YouTube URLs
- **Frame Processing**: Processes video frames for object detection

## Project Structure

```
IntelliPark/
├── ml_service/
│   ├── live2.py                # Main processing script
│   ├── parking_spaces2.json    # Parking space configuration
│   ├── requirements.txt        # Project dependencies
│   └── yolo11s.pt              # YOLO model file
└── .git/                       # Git repository
```