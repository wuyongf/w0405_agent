import subprocess
import threading
import time

class VideoRecorder:
    def __init__(self, device_index):
        self.device_index = device_index
        self.stop_flag = threading.Event()

    def update_save_path(self, output_dir):
        self.output_dir = output_dir
    
    def start_recording(self):
        command = [
            'ffmpeg',
            '-f', 'v4l2',            # Specify the input format (video4linux2 for webcams)
            '-i', f'/dev/video{self.device_index}',    # Input device (change to your device)
            '-vcodec', 'libx264',   # Video codec
            '-pix_fmt', 'yuv420p',  # Pixel format (required for compatibility)
            self.output_dir        # Output file path
        ]
        self.process = subprocess.Popen(command)

    def stop_recording(self):
        self.stop_flag.set()
        self.process.terminate()
        self.process.wait()

    def record_until_flag_set(self):
        self.start_recording()
        while not self.stop_flag.is_set():
            time.sleep(10)
            break
        self.stop_recording()

    def capture_and_save_image(self, image_path):
        # Command to capture a single frame from the video input and save it as an image
        command = [
            'ffmpeg',
            '-f', 'v4l2',                         # Specify the input format (video4linux2 for webcams)
            '-i', f'/dev/video{self.device_index}',  # Input device (change to your device)
            '-frames:v', '1',                     # Number of frames to capture (1 for a single frame)
            image_path                           # Output image file path
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
    # recorder.capture_and_save_image('image.png')