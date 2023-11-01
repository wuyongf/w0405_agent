import cv2

class RGBCamera:

    def __init__(self, index):
        self.index = index
        self.cap = cv2.VideoCapture(self.index)
        # check
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {index}.")
            pass
        # Define the codec and create VideoWriter objects for recording
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output1.avi', self.fourcc, 20.0, (640, 480))

        # logic
        self.flag = True

    def update_save_path(self, path):
        self.path = path # "/home/nw/Desktop/Videos"
        pass

    def start_recording(self):   

        while True:
            # Read frames from the first camera
            ret, frame = self.cap.read()

            # If both frames were read successfully, record them
            if ret:
                self.out.write(frame)

                # # Display the frames (optional)
                # cv2.imshow(f'Camera {self.index}', frame)

    def save_record(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        file_name = os.path.join(self.path, "recording_" + str(time.time()) + ".wav")
        sound_file = wave.open(file_name, "wb")
        sound_file.setnchannels(self.n_channels)
        sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(self.sampling_rate)
        sound_file.writeframes(b''.join(self.frames))
        sound_file.close()

        print("Saved" + file_name)

# Open the first camera
cap1 = cv2.VideoCapture(0)  # Use the appropriate index for your first camera

# Open the second camera
cap2 = cv2.VideoCapture(2)  # Use the appropriate index for your second camera

# Check if the cameras opened successfully
if not cap1.isOpened() or not cap2.isOpened():
    print("Error: Could not open one or both cameras.")
    exit(1)

# Define the codec and create VideoWriter objects for recording
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out1 = cv2.VideoWriter('output1.avi', fourcc, 20.0, (640, 480))
out2 = cv2.VideoWriter('output2.avi', fourcc, 20.0, (640, 480))

while True:
    # Read frames from the first camera
    ret1, frame1 = cap1.read()

    # Read frames from the second camera
    ret2, frame2 = cap2.read()

    # If both frames were read successfully, record them
    if ret1 and ret2:
        out1.write(frame1)
        out2.write(frame2)

        # Display the frames (optional)
        cv2.imshow('Camera 1', frame1)
        cv2.imshow('Camera 2', frame2)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and VideoWriter objects
cap1.release()
cap2.release()
out1.release()
out2.release()

# Close all OpenCV windows
cv2.destroyAllWindows()