import subprocess
import threading
import time

class VideoRecorder:
    def __init__(self, output_file):
        self.output_file = output_file
        self.stop_flag = threading.Event()

    def start_recording(self):
        command = [
            'ffmpeg',
            '-f', 'v4l2',            # Specify the input format (video4linux2 for webcams)
            '-i', '/dev/video0',    # Input device (change to your device)
            '-vcodec', 'libx264',   # Video codec
            '-pix_fmt', 'yuv420p',  # Pixel format (required for compatibility)
            self.output_file        # Output file path
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

# Example usage:y
        
recorder = VideoRecorder('output.mp4')
recorder.record_until_flag_set()
