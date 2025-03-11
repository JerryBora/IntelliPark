
import streamlit as st
import cv2
from ultralytics import YOLO
from yt_dlp import YoutubeDL
import numpy as np
import json
import os
import re
import time
from datetime import datetime

# Initialize YOLO model
model = YOLO('yolo11s.pt')

def get_available_configs():
    """Get list of all parking space configurations"""
    return sorted([f for f in os.listdir() 
                 if re.match(r'parking_spaces\d+\.json', f)])

def load_parking_spaces(selected_json):
    """Load spaces from selected JSON file"""
    if os.path.exists(selected_json):
        with open(selected_json, 'r') as f:
            return [tuple(tuple(point) for point in space) for space in json.load(f)]
    return []

def save_parking_spaces(selected_json, spaces):
    """Save to selected JSON file"""
    with open(selected_json, 'w') as f:
        json.dump([list(map(list, space)) for space in spaces], f)

def process_frame(frame, parking_spaces):
    """Process frame without scaling parking spaces"""
    results = model(frame)
    occupied = set()

    # Vehicle detection
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 2:  # Car class
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = box.conf[0]
                
                # Draw vehicle bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Car: {confidence:.2f}", 
                          (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.6, (0, 255, 0), 2)
                
                # Occupancy check
                car_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                for idx, space in enumerate(parking_spaces):
                    space_poly = np.array(space, np.int32)
                    if cv2.pointPolygonTest(space_poly, car_center, False) >= 0:
                        occupied.add(idx)

    # Draw parking spaces using original coordinates
    for idx, space in enumerate(parking_spaces):
        space_poly = np.array(space, np.int32)
        color = (0, 0, 255) if idx in occupied else (0, 255, 0)
        
        # Transparent overlay
        overlay = frame.copy()
        cv2.fillPoly(overlay, [space_poly], color)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
        
        # Polygon borders
        cv2.polylines(frame, [space_poly], True, color, 2)
        
        # Number position using original coordinates
        text_x = space[2][0] - 20  # Third point X - offset
        text_y = space[2][1] + 20  # Third point Y + offset
        cv2.putText(frame, str(idx + 1), (text_x, text_y),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame, occupied

def get_youtube_stream_url(youtube_url):
    ydl_opts = {'format': 'best'}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info['url']
    except Exception as e:
        st.error(f"YouTube Error: {str(e)}")
        return None

def main():
    st.set_page_config(layout="wide")
    st.title("Smart Parking Detection System 🚗🅿️")

    # Configuration selection
    config_files = get_available_configs()
    selected_config = st.selectbox(
        "Select Parking Configuration:",
        config_files,
        format_func=lambda x: f"Live{x[14]} Config"
    )

    # Session state initialization
    state = st.session_state
    if 'parking_spaces' not in state:
        state.parking_spaces = load_parking_spaces(selected_config)
    if 'cap' not in state:
        state.cap = None
    if 'occupied' not in state:
        state.occupied = set()
    if 'booked_spots' not in state:
        state.booked_spots = set()

    # Video input
    url = st.text_input("Enter YouTube URL:", placeholder="https://youtu.be/...")

    if url and selected_config:
        state.parking_spaces = load_parking_spaces(selected_config)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("Start/Reset Video", key="video_button"):
                if state.cap:
                    state.cap.release()
                if stream_url := get_youtube_stream_url(url):
                    state.cap = cv2.VideoCapture(stream_url)
                else:
                    st.error("Invalid URL")
            
            if state.cap and state.cap.isOpened():
                frame_placeholder = st.empty()
                metrics_placeholder = col2.empty()
                
                while state.cap.isOpened():
                    ret, frame = state.cap.read()
                    if not ret:
                        break
                    
                    processed_frame, occupied = process_frame(frame, state.parking_spaces)
                    state.occupied = occupied
                    
                    # Real-time metrics
                    with metrics_placeholder.container():
                        st.subheader("Live Status")
                        st.markdown(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
                        st.markdown("---")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Total Spaces", len(state.parking_spaces))
                        with col_b:
                            st.metric("Occupied", len(occupied))
                        
                        st.metric("Available", 
                                 len(state.parking_spaces) - len(occupied),
                                 delta_color="inverse")

                        # Parking spot status panel
                        st.markdown("---")
                        st.subheader("Spot Status")
                        for idx in range(len(state.parking_spaces)):
                            spot_id = idx + 1
                            status = "🔴" if idx in occupied else (
                                "🟡" if spot_id in state.booked_spots else "🟢"
                            )
                            btn = st.button(
                                f"{status} Spot {spot_id}",
                                key=f"spot_{spot_id}_{time.time()}",
                                help="Click to book/clear"
                            )
                            if btn:
                                if idx in occupied:
                                    st.warning("Spot occupied!")
                                elif spot_id in state.booked_spots:
                                    state.booked_spots.remove(spot_id)
                                else:
                                    state.booked_spots.add(spot_id)
                    
                    frame_placeholder.image(processed_frame, channels="BGR")
                    time.sleep(0.1)
        
        with col2:
            st.header("Controls ⚙️")
            st.markdown("---")
            if st.button("Clear Last Space"):
                if state.parking_spaces:
                    state.parking_spaces.pop()
                    save_parking_spaces(selected_config, state.parking_spaces)
                    st.rerun()
            
            st.markdown("---")
            st.info("""
            **Usage Guide:**
            1. Select config matching your camera
            2. Paste YouTube stream URL
            3. Click Start/Reset
            4. Book available spots (🟢)
            """)

if __name__ == "__main__":
    main()