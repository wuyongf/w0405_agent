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
            pass  # Keep recording until the stop flag is set
        self.stop_recording()

# Example usage:
recorder = VideoRecorder(2)
recorder.update_save_path(f'video_{time.time()}.avi')
recorder.start_recording()
time.sleep(10)
recorder.stop_recording()