import cv2
import numpy as np
import time

# Change IP & port to your DroidCam feed (replace with your phone's IP)
DROIDCAM_URL = "http://10.10.162.146:4747/video"

cap = cv2.VideoCapture(DROIDCAM_URL)

if not cap.isOpened():
    print("Error: Could not connect to DroidCam feed!")
    exit()

prev_frame = None
last_pass_time = None
rpm = 0
passes = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame not received.")
        break

    # Resize for faster processing
    frame = cv2.resize(frame, (640, 480))

    # Convert to grayscale & blur to reduce noise
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        continue

    # Frame difference
    frame_delta = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Dilate thresholded image to fill holes
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours (areas of movement)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Detect large movement near fan center
    for contour in contours:
        if cv2.contourArea(contour) > 1500:  # adjust if needed
            current_time = time.time()

            if last_pass_time is not None:
                time_diff = current_time - last_pass_time
                if time_diff > 0:
                    rpm = 60 / time_diff  # one pass per revolution
            last_pass_time = current_time

            break  # only count first large movement per frame

    # Show RPM on screen
    cv2.putText(frame, f"RPM: {int(rpm)}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw reference line in middle
    cv2.line(frame, (320, 0), (320, 480), (0, 0, 255), 2)

    cv2.imshow("Fan Speed Detection", frame)

    prev_frame = gray

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



