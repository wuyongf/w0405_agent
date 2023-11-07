# import cv2
# import os
# import time
# import threading

# class RGBCamera:
#     def __init__(self, device_index=0):
#         self.device_index = device_index
#         self.output_file = ''
#         self.record_flag = True

#         # Open the camera
#         self.cap = cv2.VideoCapture(self.device_index)
#         if not self.cap.isOpened():
#             raise Exception(f"Could not open video device {self.device_index}")

#     def update_output_info(self, output_dir, output_file_name):
#         self.output_file = os.path.join(output_dir, output_file_name)

#     def capture_and_save_video(self):

#         # Get the camera's frame width and height
#         self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#         # Define the codec and create a VideoWriter object
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs
#         self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (self.width, self.height))

#         threading.Thread(target=self.record).start()

#     def record(self):

#         while self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Display the frame
#             cv2.imshow("RGB Camera", frame)

#             # Write the frame to the video file
#             self.out.write(frame)

#             # Exit the loop when 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q') or not self.record_flag:
#                 break

#         # self.close()

#     def stop(self):
#         self.record_flag = False
#         time.sleep(1)

#     def close(self):
#         self.record_flag = False
#         time.sleep(1)
#         self.cap.release()
#         self.out.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     rgb_camera = RGBCamera()
#     rgb_camera.update_output_info(output_dir='', output_file_name='output_video.mp4')
#     rgb_camera.capture_and_save_video()
#     time.sleep(5)
#     rgb_camera.stop()
#     print('stop')
#     # rgb_camera.close()

#     rgb_camera.update_output_info(output_dir='', output_file_name='output_video2.mp4')
#     rgb_camera.capture_and_save_video()
#     time.sleep(5)
#     rgb_camera.close()


# import cv2
# import os
# import time
# import threading

# class RGBCamera:
#     def __init__(self, device_index=0):
#         self.device_index = device_index
#         self.output_file = None
#         self.out = None
#         self.record_flag = False  # Recording is off by default

#         # Open the camera
#         self.cap = cv2.VideoCapture(self.device_index)
#         if not self.cap.isOpened():
#             raise Exception(f"Could not open video device {self.device_index}")

#     def update_output_info(self, output_dir, output_file_name):
#         if self.record_flag:
#             # If recording is already in progress, stop it before starting a new one
#             self.stop_and_save_record()

#         # Set the output file
#         self.output_file = os.path.join(output_dir, output_file_name)

#     def capture_and_save_video(self):

#         # Get the camera's frame width and height
#         self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#         if self.output_file is not None:
#             # Define the codec and create a VideoWriter object
#             fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs
#             self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (self.width, self.height))
#             self.record_flag = True
#             threading.Thread(target=self.record).start()
#         else:
#             print("Output file not specified. Use update_output_info to set it.")

#     def record(self):
#         while self.cap.isOpened() and self.record_flag:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Display the frame
#             cv2.imshow("RGB Camera", frame)

#             # Write the frame to the video file
#             self.out.write(frame)

#             # Exit the loop when 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#     def stop_and_save_record(self):
#         if self.record_flag:
#             self.record_flag = False  # Stop recording
#             if self.out is not None:
#                 self.out.release()  # Release the video writer
#             cv2.destroyAllWindows()
#         else:
#             print("Recording is not in progress.")

#     def close(self):
#         if self.record_flag:
#             self.stop_and_save_record()
#         self.cap.release()

# if __name__ == "__main__":
#     rgb_camera = RGBCamera()
#     rgb_camera.update_output_info(output_dir='', output_file_name='output_video.mp4')
#     rgb_camera.capture_and_save_video()
#     time.sleep(5)
#     rgb_camera.stop_and_save_record()
#     print('First video recording stopped and saved.')

#     rgb_camera.update_output_info(output_dir='', output_file_name='output_video2.mp4')
#     rgb_camera.capture_and_save_video()
#     time.sleep(5)
#     rgb_camera.stop_and_save_record()
#     print('Second video recording stopped and saved.')

#     rgb_camera.close()


import cv2
import os
import time
import threading

class RGBCamera:
    def __init__(self, device_index=0):
        self.device_index = device_index
        self.output_file = None
        self.out = None
        self.record_flag = False  # Recording is off by default

        # Open the camera
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise Exception(f"Could not open video device {self.device_index}")

    def update_output_info(self, output_dir, output_file_name):
        if self.record_flag:
            # If recording is already in progress, stop it before starting a new one
            self.stop_and_save_record()

        # Set the output file
        self.output_file = os.path.join(output_dir, output_file_name)

    def capture_and_save_video(self):

        # Get the camera's frame width and height
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self.output_file is not None:
            # Destroy any previous OpenCV window
            cv2.destroyAllWindows()
            
            # Define the codec and create a VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can choose other codecs
            self.out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (self.width, self.height))
            self.record_flag = True
            threading.Thread(target=self.record).start()
        else:
            print("Output file not specified. Use update_output_info to set it.")

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

    def close(self):
        if self.record_flag:
            self.stop_and_save_record()
        self.cap.release()

if __name__ == "__main__":
    rgb_camera = RGBCamera()
    rgb_camera.update_output_info(output_dir='', output_file_name='output_video.mp4')
    rgb_camera.capture_and_save_video()
    time.sleep(5)
    rgb_camera.stop_and_save_record()
    print('First video recording stopped and saved.')

    rgb_camera.update_output_info(output_dir='', output_file_name='output_video2.mp4')
    rgb_camera.capture_and_save_video()
    time.sleep(5)
    rgb_camera.stop_and_save_record()
    print('Second video recording stopped and saved.')

    rgb_camera.close()

