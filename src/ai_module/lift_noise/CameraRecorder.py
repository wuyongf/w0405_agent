import cv2

# List available camera devices
for i in range(10):  # Check up to 10 camera indices, adjust as needed
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: {cap.getBackendName()}")
        cap.release()

# Initialize the USB camera
cap = cv2.VideoCapture(2)  # Use 0 for the first camera, 1 for the second, and so on

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))  # You can change the filename, codec, frame rate, and resolution

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Write the frame to the output video
    out.write(frame)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and VideoWriter objects
cap.release()
out.release()

# Close all OpenCV windows
cv2.destroyAllWindows()

#  /dev/ttyACM0
#  /dev/video0