import os
import math
import cv2
from pathlib import Path

class VideoTool:
    def __init__(self,):
        self.temp_folder = None
        pass

    def set_temp_dir(self, dir):
        self.temp_folder = dir

    def slice_video_to_images(self, video_dir, num_images = 1000, task_id = 0):
        # Create the output folder if it doesn't exist
        output_folder_dir = os.path.join(self.temp_folder, 'scrubbing')
        os.makedirs(output_folder_dir, exist_ok=True)

        # Open the video file
        cap = cv2.VideoCapture(video_dir)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate the step size to evenly divide the video into 'num_images' parts
        step = total_frames // num_images

        # Read and save frames
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Save the frame every 'step' frames
            if count % step == 0:
                resized_frame = cv2.resize(frame, (160, 120))  # Image Size.
                
                # Rotate the frame by 90 degrees clockwise
                rotated_frame = cv2.rotate(resized_frame, cv2.ROTATE_90_CLOCKWISE)
            
                image_path = os.path.join(output_folder_dir, f"{task_id}_{count//step:04d}.jpg")
                cv2.imwrite(image_path, rotated_frame)

            count += 1

        cap.release()
        cv2.destroyAllWindows()

        return output_folder_dir

    def slice_video_to_images2(self, video_dir, output_dir):
        # Create the output folder if it doesn't exist
        output_folder_dir = output_dir
        os.makedirs(output_folder_dir, exist_ok=True)

        # Open the video file
        cap = cv2.VideoCapture(video_dir)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read and save frames
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Save each frame as an image
            resized_frame = cv2.resize(frame, (320, 240))  # Image Size.
            # Rotate the frame by 90 degrees clockwise
            rotated_frame = cv2.rotate(resized_frame, cv2.ROTATE_90_CLOCKWISE)
            
            image_path = os.path.join(output_folder_dir, f"{count:04d}.jpg")
            cv2.imwrite(image_path, rotated_frame)

            count += 1

        cap.release()
        # cv2.destroyAllWindows()

        return output_folder_dir

    def slowdown_video(self, input_file, slowdown_factor=2):
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
        output_file_dir = os.path.join(self.temp_folder, "slowdown.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(output_file_dir, fourcc, new_fps, (width, height))
        
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
        
        # print("Video processing completed.")
        return output_file_dir

    def get_video_duration(self, video_dir):
        cap = cv2.VideoCapture(video_dir)
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

if __name__ == '__main__':
    
    video_tool = VideoTool()
    video_tool.set_temp_dir('result')

    video_dir = 'data/video_1709898640.608474.avi'

    video_duration = video_tool.get_video_duration(video_dir)
    print(video_duration)

    slowdown_video_dir = video_tool.slowdown_video(video_dir)
    print(slowdown_video_dir)

    res = video_tool.slice_video_to_images(slowdown_video_dir)
    print(res)
    
    pass