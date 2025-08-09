import cv2
import numpy as np
import time
import math
import cv2

ip = "10.10.162.146"  # Your phone's IP
port = 4747           # Default DroidCam port
url = f"http://{ip}:{port}/video"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: Could not connect to DroidCam feed!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("DroidCam Feed", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


# --- Parameters ---
ROI_RADIUS = 200  # radius for fan area detection (adjust based on camera distance)
SMOOTHING_FACTOR = 0.9  # for stabilizing RPM values

# ---- CHANGE THIS to your DroidCam IP ----
DROIDCAM_URL = "http://10.10.162.146:4747/video"  # Replace with your IP from DroidCam
cap = cv2.VideoCapture(DROIDCAM_URL)

if not cap.isOpened():
    print("Error: Could not connect to DroidCam feed!")
    exit()

# Read first frame
ret, prev_frame = cap.read()
if not ret:
    print("Error: Unable to read video feed.")
    exit()

# Convert to grayscale
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Center of the frame (assume fan is roughly at center)
frame_h, frame_w = prev_gray.shape
cx, cy = frame_w // 2, frame_h // 2

# RPM tracking
last_rpm = 0
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create mask for circular ROI around the fan
    mask = np.zeros_like(gray)
    cv2.circle(mask, (cx, cy), ROI_RADIUS, 255, -1)
    masked_gray = cv2.bitwise_and(gray, mask)
    masked_prev_gray = cv2.bitwise_and(prev_gray, mask)

    # Calculate dense optical flow
    flow = cv2.calcOpticalFlowFarneback(
        masked_prev_gray, masked_gray,
        None, 0.5, 3, 15, 3, 5, 1.2, 0
    )

    # Get magnitude and angle of flow vectors
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # Mean angular velocity (degrees per second)
    if np.any(mag > 1):
        mean_ang_vel = np.mean(ang[mag > 1])
    else:
        mean_ang_vel = 0

    # Convert angular velocity to RPM
    rpm = (mean_ang_vel * 180 / math.pi) / 360 * 60

    # Smooth RPM reading
    rpm = SMOOTHING_FACTOR * last_rpm + (1 - SMOOTHING_FACTOR) * rpm
    last_rpm = rpm

    # Draw ROI circle
    cv2.circle(frame, (cx, cy), ROI_RADIUS, (0, 255, 0), 2)

    # Display RPM
    cv2.putText(frame, f"Fan Speed: {rpm:.1f} RPM",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 255), 2)

    cv2.imshow("Fan Speed Detector", frame)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()



