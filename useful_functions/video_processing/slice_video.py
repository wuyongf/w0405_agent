import cv2
import os

def slice_video_to_images(video_path, output_folder, num_images):
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
            image_path = os.path.join(output_folder, f"516_{count//step:04d}.jpg")
            cv2.imwrite(image_path, frame)

        count += 1

    cap.release()
    cv2.destroyAllWindows()

# Example usage
video_path = "data/516/video_1709898640.608474.avi"
output_folder = "result/output_516_fps4"
num_images = 320  # Change this to the number of images you want
slice_video_to_images(video_path, output_folder, num_images)