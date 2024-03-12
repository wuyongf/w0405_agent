import cv2
import os
from pathlib import Path

def slice_video_to_images(video_path, output_folder, num_images, task_id):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
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
            image_path = os.path.join(output_folder, f"{task_id}_{count//step:04d}.jpg")
            cv2.imwrite(image_path, frame)

        count += 1

    cap.release()
    cv2.destroyAllWindows()

# Example usage
task_id = 514
fps = 4

target_folder = Path(f"data/{task_id}")
video_path = None
for file in target_folder.rglob("*"):
    video_path = str(file)
    print(video_path)
# video_path = f"data/{task_id}/video_1708683378.6543932.mp4"
output_folder = f"result/output_{task_id}_fps{fps}"
num_images = fps * 60  # Change this to the number of images you want
slice_video_to_images(video_path, output_folder, num_images, task_id)