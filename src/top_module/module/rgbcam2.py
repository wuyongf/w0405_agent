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
        # if not os.path.exists(output_dir):
        #     os.makedirs(output_dir, exist_ok=True)

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
                cv2.imshow('Frame', frame)
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
    ### Video Recording
    rgb_camera = RGBCamRecorder(device_index=2)
    rgb_camera.update_save_path(output_dir='')
    rgb_camera.capture_and_save_video()
    time.sleep(20)
    rgb_camera.stop_and_save_record()
    print('First video recording stopped and saved.')

    # rgb_camera.update_output_info(output_dir='', output_file_name='output_video2.mp4')
    # rgb_camera.capture_and_save_video()
    # time.sleep(5)
    # rgb_camera.stop_and_save_record()
    # print('Second video recording stopped and saved.')

    rgb_camera.close()