import os
import subprocess
import threading
import time

class RGBCamRecorder:
    def __init__(self, device_index):
        self.device_index = device_index
        self.stop_flag = threading.Event()
        self.output_file = None

    def update_save_path(self, output_dir):
        self.output_dir = output_dir
    
    # start_recording
    def capture_and_save_video(self,resolution = '1280x720', fps=10):
        output_file_name = f'video_{time.time()}.avi'
        self.output_file = os.path.join(self.output_dir, output_file_name)
        command = [
            'ffmpeg',
            '-f', 'v4l2',            # Specify the input format (video4linux2 for webcams)
            '-video_size', resolution,              # Specify the resolution
            '-framerate', str(fps),                 # Specify the frames per second
            '-i', f'/dev/video{self.device_index}',    # Input device (change to your device)
            '-vcodec', 'libx264',   # Video codec
            '-pix_fmt', 'yuv420p',  # Pixel format (required for compatibility)
            self.output_file        # Output file path
        ]
        self.process = subprocess.Popen(command)

    # stop_recording
    def stop_and_save_record(self):
        self.stop_flag.set()
        self.process.terminate()
        self.process.wait()
        return self.output_file

    def record_until_flag_set(self):
        self.start_recording()
        while not self.stop_flag.is_set():
            time.sleep(10)
            break
        self.stop_recording()


    ### [Image]
    def update_cap_save_path(self, cap_save_dir):
        self.cap_save_dir = cap_save_dir
        os.makedirs(self.cap_save_dir, exist_ok=True)

    def cap_rgb_img(self, image_name):
        # Command to capture a single frame from the video input and save it as an image
        image_filename = os.path.join(self.cap_save_dir, image_name)
        command = [
            'ffmpeg',
            '-f', 'v4l2',                         # Specify the input format (video4linux2 for webcams)
            '-i', f'/dev/video{self.device_index}',  # Input device (change to your device)
            '-frames:v', '1',                     # Number of frames to capture (1 for a single frame)
            image_filename                           # Output image file path
        ]
        # Run the FFmpeg command to capture and save the image
        subprocess.run(command)

if __name__ == "__main__":

    # Example usage:
    recorder = VideoRecorder(2)
    recorder.update_save_path(f'video_{time.time()}.avi')
    recorder.start_recording()
    time.sleep(10)
    recorder.stop_recording()

    # # [Capture and save an image]
    # recorder.cap_rgb_img('image.png')