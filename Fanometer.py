import cv2
import numpy as np
import time
import math

# Parameters
ROI_RADIUS = 200
SMOOTHING_FACTOR = 0.85
DROIDCAM_URL = "http://10.10.162.146:4747/video"

# Capture
cap = cv2.VideoCapture(DROIDCAM_URL)
if not cap.isOpened():
    print("Error: Could not connect to DroidCam feed!")
    exit()

ret, prev_frame = cap.read()
if not ret:
    print("Error: Unable to read video feed.")
    exit()

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
frame_h, frame_w = prev_gray.shape
cx, cy = frame_w // 2, frame_h // 2

last_rpm = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ROI Mask
    mask = np.zeros_like(gray)
    cv2.circle(mask, (cx, cy), ROI_RADIUS, 255, -1)
    masked_gray = cv2.bitwise_and(gray, mask)
    masked_prev_gray = cv2.bitwise_and(prev_gray, mask)

    # Optical Flow
    flow = cv2.calcOpticalFlowFarneback(
        masked_prev_gray, masked_gray,
        None, 0.5, 3, 15, 3, 5, 1.2, 0
    )

    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # Estimate RPM
    if np.any(mag > 1):
        mean_ang = np.mean(ang[mag > 1])
    else:
        mean_ang = 0

    rpm = (mean_ang * 180 / math.pi) / 360 * 60
    rpm = SMOOTHING_FACTOR * last_rpm + (1 - SMOOTHING_FACTOR) * rpm
    last_rpm = rpm

    # Display
    cv2.circle(frame, (cx, cy), ROI_RADIUS, (0, 255, 0), 2)
    cv2.putText(frame, f"Fan Speed: {rpm:.1f} RPM",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 255), 2)
    cv2.imshow("Fan Speed Detector", frame)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()





