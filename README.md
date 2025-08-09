# 🌀 Fanometer

Fanometer is a Python + OpenCV project that measures the **rotations per minute (RPM)** of a fan in real time using your phone's camera as a video feed via **DroidCam**.  
It uses **Optical Flow** to detect motion and estimate the fan's speed.

---

## 📸 How It Works
1. Connect your phone's camera to your computer using **DroidCam** (Wi-Fi or USB).
2. The script processes the live video feed using **OpenCV**.
3. It applies **Farneback Optical Flow** to detect rotational motion in a circular region.
4. Calculates and displays the **estimated RPM** of the fan.

---

## ⚙️ Requirements
- Python 3.7+
- OpenCV
- NumPy
- DroidCam app (on phone)
- PC DroidCam client (for Windows/Linux/Mac)

---

## 📦 Installation
1. **Clone this repository**:
   ```bash
   git clone https://github.com/poojasnair2428/Fanometer.git
   cd Fanometer
