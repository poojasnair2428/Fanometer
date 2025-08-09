import cv2
import numpy as np
import time
import math

# ------------------ SETTINGS ------------------
BLADE_COUNT = 3  # Fan blades
THRESHOLD = 25
REF_LINE_POS = 200
MAX_RPM = 700  # For gauge scaling
# ------------------------------------------------

cap = cv2.VideoCapture(0)

# For motion detection
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

pass_times = []
last_pass_time = None
rpm = 0

def get_funny_label(rpm):
    if rpm < 80:
        return "Retirement Mode 💤"
    elif rpm < 200:
        return "Tea Stall Breeze 🍵"
    elif rpm < 350:
        return "Ceiling Cyclone 🌪️"
    elif rpm < 500:
        return "Helicopter Training 🚁"
    else:
        return "Warp Speed ⚡"

def draw_gauge(frame, rpm):
    center = (150, 350)
    radius = 100

    # Draw gauge arc
    cv2.ellipse(frame, center, (radius, radius), 0, 180, 0, (200, 200, 200), 3)

    # Needle angle (180 deg = 0 RPM, 0 deg = MAX_RPM)
    angle = 180 - (rpm / MAX_RPM) * 180
    angle = max(0, min(180, angle))

    # Needle endpoint
    end_x = int(center[0] + radius * math.cos(math.radians(angle)))
    end_y = int(center[1] - radius * math.sin(math.radians(angle)))
    cv2.line(frame, center, (end_x, end_y), (0, 0, 255), 3)

    # Center dot
    cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # Labels
    cv2.putText(frame, f"{rpm:.1f} RPM", (center[0]-50, center[1]+60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, THRESHOLD, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.line(frame, (0, REF_LINE_POS), (frame.shape[1], REF_LINE_POS), (0, 255, 0), 2)

    blade_detected = False
    for cnt in contours:
        if cv2.contourArea(cnt) > 5000:
            x, y, w, h = cv2.boundingRect(cnt)
            if y < REF_LINE_POS < y + h:
                blade_detected = True
                break

    if blade_detected and (last_pass_time is None or time.time() - last_pass_time > 0.1):
        current_time = time.time()
        if last_pass_time is not None:
            pass_times.append(current_time - last_pass_time)
            if len(pass_times) > 10:
                pass_times.pop(0)
            avg_pass_time = np.mean(pass_times)
            rpm = (60 / (avg_pass_time * BLADE_COUNT))
        last_pass_time = current_time

    # Funny label
    label = get_funny_label(rpm)
    cv2.putText(frame, label, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 0), 2)

    # Draw the speedometer gauge
    draw_gauge(frame, rpm)

    cv2.imshow("Ceiling Fan Speed Tracker", frame)
    prev_gray = gray.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
