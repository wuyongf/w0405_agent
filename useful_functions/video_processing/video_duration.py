import cv2
import math

def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    
    # Get the total number of frames and frame rate
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate duration in seconds
    duration_sec = math.floor(frame_count / fps)
    
    # Release the video capture object
    cap.release()
    
    return duration_sec

# Example usage:
video_path = 'data/516/video_1709898640.608474.avi'
duration_sec = get_video_duration(video_path)
if duration_sec is not None:
    print(f"Video duration: {duration_sec:.2f} seconds")