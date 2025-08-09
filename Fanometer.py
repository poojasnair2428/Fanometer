import cv2
import numpy as np
import math
import sys

# ------------------ USER SETTINGS ------------------
VIDEO_PATH = "C:/Users/hp/Downloads/fanreal.mp4"   # <--- put your recorded file name here
BLADE_COUNT = 3          # your fan has 3 blades
THRESHOLD = 25           # motion sensitivity (lower = more sensitive)
REF_LINE_POS = 200       # y coordinate of reference line (tweak to where blades pass)
MIN_CONTOUR_AREA = 4000  # ignore smaller motion blobs
COOLDOWN_FRAMES = 5      # frames to skip after a detected pass to avoid duplicates
MAX_HISTORY = 10         # how many pass intervals to average
MAX_RPM = 700            # gauge upper bound
LOOP_VIDEO = True        # if True, loops the video for continuous demo
# ---------------------------------------------------

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"ERROR: Could not open video file '{VIDEO_PATH}'")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Read first frame for initialization
ret, prev_frame = cap.read()
if not ret:
    print("ERROR: Video appears empty.")
    sys.exit(1)

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

pass_frame_idxs = []
last_pass_frame = -9999
rpm = 0.0
frame_idx = 0

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
    center = (150, height - 100)
    radius = 100
    # Gauge arc (semi-circle)
    cv2.ellipse(frame, center, (radius, radius), 0, 180, 0, (200, 200, 200), 4)

    # Clamp rpm to [0, MAX_RPM]
    clamped = max(0, min(MAX_RPM, rpm))
    # Angle: 180 degrees (left) -> 0 RPM, 0 degrees (right) -> MAX_RPM
    angle = 180 - (clamped / MAX_RPM) * 180
    angle = max(0, min(180, angle))
    end_x = int(center[0] + radius * math.cos(math.radians(angle)))
    end_y = int(center[1] - radius * math.sin(math.radians(angle)))
    cv2.line(frame, center, (end_x, end_y), (0, 0, 255), 4)
    cv2.circle(frame, center, 6, (0, 0, 255), -1)
    cv2.putText(frame, f"{rpm:.1f} RPM", (center[0]-60, center[1]+70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

print(f"Video opened: {VIDEO_PATH} | FPS={fps:.2f} | Frames={frame_count} | WxH={width}x{height}")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        if LOOP_VIDEO:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame_idx = 0
            ret, frame = cap.read()
            if not ret:
                break
        else:
            break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Frame difference motion detection
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, THRESHOLD, 255, cv2.THRESH_BINARY)
    # Optional morphology to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel, iterations=1)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw reference line where we expect blades to cross
    cv2.line(frame, (0, REF_LINE_POS), (width, REF_LINE_POS), (0, 255, 0), 2)

    blade_detected = False
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_CONTOUR_AREA:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        # draw bounding box for debugging
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        # if bounding box crosses reference line, count as a blade pass
        if y < REF_LINE_POS < y + h:
            # ensure cooldown frames to avoid duplicate counts
            if frame_idx - last_pass_frame > COOLDOWN_FRAMES:
                blade_detected = True
                break

    if blade_detected:
        # record frame index of pass
        pass_frame_idxs.append(frame_idx)
        last_pass_frame = frame_idx
        # keep only last MAX_HISTORY intervals
        if len(pass_frame_idxs) > (MAX_HISTORY + 1):
            pass_frame_idxs.pop(0)

        # compute average interval (seconds) between consecutive passes
        if len(pass_frame_idxs) >= 2:
            intervals_frames = np.diff(pass_frame_idxs)  # frames between passes
            # convert frames -> seconds using fps
            intervals_seconds = intervals_frames / fps
            avg_pass_time = intervals_seconds.mean()
            # RPM formula: passes per second -> divide by blades to get revolutions per second
            # RPM = revs_per_sec * 60 ; revs_per_sec = (1 / avg_pass_time) / BLADE_COUNT
            if avg_pass_time > 0:
                rpm = (60.0 / (avg_pass_time * BLADE_COUNT))
            else:
                rpm = 0.0

    # overlay funny label and gauge
    label = get_funny_label(rpm)
    cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,165,255), 2)
    draw_gauge(frame, rpm)

    # small debug: show current frame index and passes counted
    cv2.putText(frame, f"Frame: {frame_idx}", (20, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
    cv2.putText(frame, f"Passes: {len(pass_frame_idxs)}", (140, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

    cv2.imshow("Ceiling Fan Speed Tracker (video)", frame)

    prev_gray = gray.copy()
    frame_idx += 1

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
