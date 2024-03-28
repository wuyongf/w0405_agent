import cv2
import os
import time
from threading import Thread, Event

class RGBCamRecorder:
    def __init__(self, device_index):
        self.device_index = device_index
        self.output_file = None
        self.output_dir = ""
        self.cap_save_dir = ""
        self.record_flag = Event()
        self.thread = None
        self.cap = None
        self.out = None

    def update_save_path(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    def capture_and_save_video(self):
        self.cap_open_cam()
        output_file_name = f'video_{time.time()}.avi'
        self.output_file = os.path.join(self.output_dir, output_file_name)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter(self.output_file, fourcc, 15.0, (1280, 720))
        self.record_flag.set()
        self.thread = Thread(target=self.record)
        self.thread.start()

    def record(self):
        while self.record_flag.is_set():
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
            else:
                print("Failed to capture frame")
                break
        self.cleanup()

    def stop_and_save_record(self):
        self.record_flag.clear()
        if self.thread is not None:
            self.thread.join()
        return self.output_file

    def cleanup(self):
        if self.out is not None:
            self.out.release()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def close(self):
        self.stop_and_save_record()
        self.cleanup()

    ### Image
    def update_cap_save_path(self, cap_save_dir):
        self.cap_save_dir = cap_save_dir
        os.makedirs(self.cap_save_dir, exist_ok=True)
        
    def cap_open_cam(self):
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video device {self.device_index}")

    def cap_rgb_img(self, image_name):
        ret, frame = self.cap.read()
        if not ret:
            print("Error reading frame from camera.")
            return

        image_filename = os.path.join(self.cap_save_dir, image_name)
        cv2.imwrite(image_filename, frame)

# Example usage
if __name__ == '__main__':
    camera_index = 0  # Adjust as needed
    save_directory = 'path/to/save/videos'  # Adjust as needed
    cap_save_directory = 'path/to/save/images'  # Adjust as needed
    image_name = 'captured_image.jpg'  # Adjust as needed
    
    recorder = RGBCamRecorder(camera_index)
    recorder.update_save_path(save_directory)
    recorder.update_cap_save_path(cap_save_directory)

    try:
        recorder.capture_and_save_video()
        # Optionally capture an image during recording
        recorder.cap_rgb_img(image_name)
        time.sleep(60)  # Record for 60 seconds as an example
    finally:
        recorder.close()