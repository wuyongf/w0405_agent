import cv2
import threading

class RGBCamera:

    def __init__(self, index):
        self.index = index
        self.cap = cv2.VideoCapture(self.index)
        
        # Check if the camera is opened
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {index}.")
            return
        
        # Define the codec and create VideoWriter objects for recording
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = None  # This will be initialized in start_recording method
        
        # Logic
        self.record_flag = False  # Recording is off by default

    def update_save_path(self, path):
        # Set the output file path for video recording
        self.out = cv2.VideoWriter(path, self.fourcc, 20.0, (640, 480))

    def start_recording(self):
        # Start recording video
        if self.out is not None and not self.record_flag:
            self.record_flag = True
            threading.Thread(target=self.record).start() 

    def stop_and_save_record(self):
        # Stop recording and save the recorded video
        if self.record_flag:
            self.record_flag = False
            self.out.release()  # Release the video writer

    def record(self):
        while True:
            if self.record_flag:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame.")
                    break
                self.out.write(frame)  # Write the frame to the video file

    def release(self):
        # Release the video capture and writer objects
        self.cap.release()
        if self.out is not None:
            self.out.release()

if __name__ == "__main__":
    camera = RGBCamera(0)  # Initialize camera with index 0
    camera.update_save_path('output1.avi')  # Set the output file path
    camera.start_recording()  # Start recording

    # You can stop recording and save the video using the following line if needed
    # camera.stop_and_save_record()

    # Don't forget to release the camera at the end
    # camera.release()
