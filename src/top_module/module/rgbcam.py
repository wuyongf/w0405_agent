import cv2
import os
import time
import threading

class RGBCamRecorder:
    def __init__(self, device_index=0):
        self.device_index = device_index
        self.output_file = None
        self.out = None
        self.record_flag = False  # Recording is off by default
        
        # # Create a lock for synchronizing access to the camera
        # self.lock = threading.Lock()

    def update_save_path(self, output_dir):
        if self.record_flag:
            # If recording is already in progress, stop it before starting a new one
            self.stop_and_save_record()

        # Set the output file
        self.output_dir = output_dir

    def capture_and_save_video(self):

        # Open the camera
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video device {self.device_index}")

        # Get the camera's frame width and height
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_file_name = 'video_' + str(time.time()) + '.mp4'
        self.output_file = os.path.join(self.output_dir, output_file_name)

        if self.output_file is not None:
            # Destroy any previous OpenCV window
            cv2.destroyAllWindows()
            
            # Define the codec and create a VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs
            self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (self.width, self.height))
            self.record_flag = True
            threading.Thread(target=self.record).start()
        else:
            print("Output file not specified. Use update_save_path to set it.")

    def record(self):
        while self.cap.isOpened() and self.record_flag:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Display the frame
            cv2.imshow("RGB Camera", frame)

            # Write the frame to the video file
            self.out.write(frame)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def stop_and_save_record(self):
        if self.record_flag:
            self.record_flag = False  # Stop recording
            if self.out is not None:
                self.out.release()  # Release the video writer
            cv2.destroyAllWindows()
        else:
            print("Recording is not in progress.")

        return self.output_file

    def close(self):
        if self.record_flag:
            self.stop_and_save_record()
        self.cap.release()


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

    # def start_cap_img(self, output_folder):
    #     self.record_flag = True
    #     self.cap_rgb_img(output_folder)

    # def stop_cap_img(self):
    #     self.record_flag = False

def process_record():
    rgb_camera = RGBCamRecorder(device_index=2)
    rgb_camera.update_cap_save_path('test')
    rgb_camera.cap_open_cam()
    while(True):
        rgb_camera.cap_rgb_img('002.jpg')
        time.sleep(1)

if __name__ == "__main__":

    #### Video Recording
    # rgb_camera = RGBCamRecorder(device_index=0)
    # rgb_camera.update_save_path(output_dir='', output_file_name='video_000.999.mp4')
    # rgb_camera.capture_and_save_video()
    # time.sleep(60)
    # rgb_camera.stop_and_save_record()
    # print('First video recording stopped and saved.')

    # # rgb_camera.update_output_info(output_dir='', output_file_name='output_video2.mp4')
    # # rgb_camera.capture_and_save_video()
    # # time.sleep(5)
    # # rgb_camera.stop_and_save_record()
    # # print('Second video recording stopped and saved.')

    # rgb_camera.close()

    from multiprocessing import Process
    process = Process(target=process_record, args=())
    process.start()

    # #### Image Capture
    # rgb_camera = RGBCamRecorder(device_index=2)
    # rgb_camera.update_cap_save_path('test')
    # rgb_camera.cap_open_cam()
    # rgb_camera.cap_rgb_img('001.jpg')

