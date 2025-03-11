
# IntelliPark - Technical Documentation

This document provides detailed technical information about the functions and components used in the `live2.py` script, which is part of the IntelliPark Smart Parking Detection System.

## Overview of `live2.py`

`live2.py` is a configuration and testing tool for the IntelliPark system. It allows users to:
1. Connect to YouTube video streams
2. Define parking spaces by drawing polygons
3. Test vehicle detection and parking space occupancy in real-time
4. Save parking space configurations for use in the main application

## Dependencies

- **OpenCV (cv2)**: Used for image processing, drawing, and video capture
- **Ultralytics YOLO**: Provides the object detection model
- **yt-dlp**: Extracts video streams from YouTube URLs
- **NumPy**: Handles array operations for image processing
- **JSON**: Manages serialization and deserialization of parking space data

## Core Components

### YOLO Model Initialization

``` model = YOLO('yolo11s.pt') ```

The script initializes the YOLO (You Only Look Once) object detection model using a pre-trained weights file (`yolo11s.pt`). This model is responsible for detecting vehicles in video frames.

### Parking Space Management Functions

#### `load_parking_spaces()`

```python
def load_parking_spaces():
    if os.path.exists('parking_spaces2.json'):
        with open('parking_spaces2.json', 'r') as f:
            parking_spaces_loaded = json.load(f)
            return [tuple(tuple(point) for point in space) for space in parking_spaces_loaded]
    else:
        return []  # Start with an empty list of parking spaces
```

**Purpose**: Loads previously defined parking spaces from a JSON file.
**Parameters**: None
**Returns**: A list of parking spaces, where each space is represented as a tuple of coordinate points.
**Behavior**:
- Checks if the configuration file exists
- If it exists, loads and deserializes the JSON data
- Converts the loaded data into tuples for internal representation
- Returns an empty list if no configuration file is found

#### `save_parking_spaces()`

```python
def save_parking_spaces():
    parking_spaces_serializable = [[list(point) for point in space] for space in parking_spaces]
    with open('parking_spaces2.json', 'w') as f:
        json.dump(parking_spaces_serializable, f)
```

**Purpose**: Saves the current parking space configuration to a JSON file.
**Parameters**: None
**Returns**: None
**Behavior**:
- Converts the tuple-based parking space representation to a list-based format for JSON serialization
- Writes the serialized data to the configuration file

#### `clear_last_parking_space()`

```python
def clear_last_parking_space():
    global parking_spaces
    if parking_spaces:
        removed_space = parking_spaces.pop()
        save_parking_spaces()
        print(f"Last parking space {len(parking_spaces) + 1} cleared: {removed_space}")
    else:
        print("No parking spaces to clear.")
```

**Purpose**: Removes the most recently added parking space.
**Parameters**: None
**Returns**: None
**Behavior**:
- Removes the last parking space from the global list if any spaces exist
- Saves the updated configuration
- Provides user feedback via console output

### User Interaction

#### `mouse_callback(event, x, y, flags, param)`

```python
def mouse_callback(event, x, y, flags, param):
    global current_points, adding_space, parking_spaces
    if event == cv2.EVENT_LBUTTONDOWN and adding_space:
        current_points.append((x, y))
        print(f"Point {len(current_points)}: ({x}, {y})")
        
        if len(current_points) == 4:
            new_space = tuple(current_points)
            parking_spaces.append(new_space)
            save_parking_spaces()
            print(f"Parking space {len(parking_spaces)} added and saved.")
            current_points.clear()
            adding_space = False
```

**Purpose**: Handles mouse click events for defining parking spaces.
**Parameters**:
- `event`: The type of mouse event (e.g., click, move)
- `x`, `y`: The coordinates of the mouse pointer
- `flags`: Additional flags for the event
- `param`: Additional parameters

**Returns**: None
**Behavior**:
- Activates only when the user is in "adding space" mode and clicks the left mouse button
- Records the clicked point coordinates
- After collecting 4 points (to form a quadrilateral), creates a new parking space
- Saves the updated configuration and resets the interaction state

### YouTube Integration

#### `get_youtube_stream_url(youtube_url)`

```python
def get_youtube_stream_url(youtube_url):
    ydl_opts = {'format': 'best'}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']
```

**Purpose**: Extracts the direct video stream URL from a YouTube video link.
**Parameters**:
- `youtube_url`: The URL of the YouTube video

**Returns**: The direct video stream URL that can be used with OpenCV's VideoCapture
**Behavior**:
- Uses yt-dlp to extract video information without downloading
- Requests the best quality format available
- Returns the direct URL to the video stream

### Main Processing Loop

The main loop in `live2.py` performs several key operations:

1. **Frame Capture and Preprocessing**:
   - Reads frames from the video stream
   - Resizes frames for performance optimization
   - Implements frame skipping to reduce processing load

2. **Vehicle Detection**:
   - Processes each frame with the YOLO model
   - Identifies vehicles (class ID 2 for cars)
   - Draws bounding boxes around detected vehicles

3. **Parking Space Occupancy Analysis**:
   - For each detected vehicle, calculates its center point
   - Checks if the center point falls within any defined parking space
   - Marks spaces as occupied when containing a vehicle center

4. **Visualization**:
   - Draws parking spaces with color coding (green for available, red for occupied)
   - Creates semi-transparent overlays for better visibility
   - Displays space numbers and occupancy statistics
   - Shows interactive elements during space definition

5. **User Input Handling**:
   - Processes keyboard commands:
     - 'A': Enter parking space addition mode
     - 'C': Clear the last defined parking space
     - 'Q': Quit the application

## Global Variables

- `parking_spaces`: List of all defined parking spaces
- `current_points`: Temporary storage for points being defined
- `adding_space`: Boolean flag indicating if the user is currently adding a space

## Technical Implementation Details

### Parking Space Representation

Each parking space is represented as a tuple of 4 coordinate points, defining a quadrilateral. The points are stored in clockwise or counter-clockwise order to form a closed polygon.

### Occupancy Detection Algorithm

The script uses a point-in-polygon test to determine if a vehicle occupies a parking space:
1. For each detected vehicle, the center point is calculated
2. For each parking space, the `cv2.pointPolygonTest()` function checks if the vehicle's center point lies within the space's polygon
3. If the test returns a non-negative value, the space is marked as occupied

### Visualization Techniques

- **Transparent Overlays**: Created by blending two images with `cv2.addWeighted()`
- **Polygon Drawing**: Uses `cv2.fillPoly()` for the space interior and `cv2.polylines()` for borders
- **Status Display**: Dynamic text rendering with `cv2.putText()` showing occupancy statistics

### Performance Optimizations

- **Frame Skipping**: Processes only every nth frame to reduce computational load
- **Frame Resizing**: Reduces the frame dimensions to speed up processing
- **Efficient Data Structures**: Uses sets for tracking occupied spaces

## Usage Scenarios

### Parking Space Configuration

1. Launch the script with a YouTube URL of a parking lot
2. Press 'A' to enter space addition mode
3. Click to define the 4 corners of each parking space
4. Spaces are automatically saved to the configuration file

### Testing Detection Accuracy

1. Load a previously configured parking lot
2. Observe the real-time detection of vehicles and occupancy status
3. Adjust parking space definitions if needed using the 'C' key to remove inaccurate spaces

## Error Handling

The script includes basic error handling for:
- Video stream connection failures
- Frame reading errors
- Invalid parking space definitions
- Drawing errors

## Limitations

- Requires clear visibility of parking spaces
- Performance depends on the quality of the video stream
- Detection accuracy may be affected by lighting conditions, occlusions, or unusual vehicle positions
- Currently supports only rectangular or quadrilateral parking space shapes
