import cv2

def slow_down_video(input_file, output_file, slowdown_factor=2):
    # Open the input video
    cap = cv2.VideoCapture(input_file)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get the original video's frame rate and frame size
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate the new frame rate (original frame rate divided by the slowdown factor)
    new_fps = fps / slowdown_factor
    
    # Define the codec and create a VideoWriter object to save the output video
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_file, fourcc, new_fps, (width, height))
    
    # Read and write frames one by one, effectively slowing down the video
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            out.write(frame)  # Write the frame to the output video
        else:
            break  # Break the loop if there are no more frames to read

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print("Video processing completed.")

# Example usage
input_video_path = 'data/516/video_1709898640.608474.avi'
output_video_path = 'result/slowdown/516/video_1709898640.608474.mkv'
slow_down_video(input_video_path, output_video_path, slowdown_factor=2)