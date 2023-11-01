import cv2

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