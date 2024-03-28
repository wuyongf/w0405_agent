import cv2
import os
import time
from multiprocessing import Process, Value
import ctypes

class RGBCamRecorder:
    def __init__(self, device_index):
        self.device_index = device_index
        self.output_file = None
        self.output_dir = ""
        self.record_flag = Value(ctypes.c_bool, False)
        self.process = None
        self.cap = None
        self.out = None

    def update_save_path(self, output_dir):
        # Ensure the recording is stopped before updating save path
        if self.record_flag.value:
            self.stop_and_save_record()
        self.output_dir = output_dir

    def capture_and_save_video(self):
        # Initialize camera and video writer
        self.cap = cv2.VideoCapture(self.device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 15)

        if not self.cap.isOpened():
            raise Exception(f"Could not open video device {self.device_index}")

        output_file_name = f'video_{int(time.time())}.avi'  # Use int for filename
        self.output_file = os.path.join(self.output_dir, output_file_name)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.output_file, fourcc, 15.0, (1280, 720))

        # Start recording process
        self.record_flag.value = True
        self.process = Process(target=self.record)
        self.process.start()

    def record(self):
        # Recording loop
        while self.record_flag.value:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
            else:
                break
        self.cleanup()

    def stop_and_save_record(self):
        # Signal to stop and wait for the process to finish
        self.record_flag.value = False
        if self.process is not None:
            self.process.join()
        self.cleanup()  # Ensure resources are released properly

    def cleanup(self):
        # Release resources in the right order
        if self.out is not None:
            self.out.release()
            self.out = None  # Reset the writer to avoid potential double release
        if self.cap is not None:
            self.cap.release()
            self.cap = None  # Reset the capture device
        cv2.destroyAllWindows()

    def close(self):
        # Ensure the stop_and_save_record is called correctly
        self.stop_and_save_record()

    ### Image
    def update_cap_save_path(self, cap_save_dir):
        self.cap_save_dir = cap_save_dir
        os.makedirs(self.cap_save_dir, exist_ok=True)
    
    def cap_open_cam(self):
        # Open the camera
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video device {self.device_index}")
 
    def cap_rgb_img(self, image_name):
        # Capture and save an image
        ret, frame = self.cap.read()
        if not ret:
            print("Error reading frame from camera.")
            return

        # Save the image
        image_filename = os.path.join(self.cap_save_dir, image_name)
        cv2.imwrite(image_filename, frame)

def process_record():
    rgb_camera = RGBCamRecorder(device_index=2)
    rgb_camera.update_cap_save_path('test')
    rgb_camera.cap_open_cam()
    while(True):
        rgb_camera.cap_rgb_img('002.jpg')
        time.sleep(1)

if __name__ == "__main__":

    #### Video Recording
    rgb_camera = RGBCamRecorder(device_index=0)
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

    # from multiprocessing import Process
    # process = Process(target=process_record, args=())
    # process.start()

    # #### Image Capture
    # rgb_camera = RGBCamRecorder(device_index=0)
    # rgb_camera.update_cap_save_path('test')
    # rgb_camera.cap_open_cam()
    # rgb_camera.cap_rgb_img('003.jpg')

    pass

