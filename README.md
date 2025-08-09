# 🌀 Fanometer


Fanometer is a Python + Opencv program that attempts to measure the RPM (rotations per minute) of a fan using your phone camera feed through DroidCam. It detects motion in a circular area and estimates speed using optical flow calculations.
While it’s a neat computer vision experiment, it’s essentially **useless** in practical terms — the readings are not accurate and can be easily thrown off by lighting, camera angle, or background movement.

---

## The Problem Statement

Measuring fan speed usually requires specialized tools like tachometers. Using a camera to calculate RPM might sound cool, but it’s highly unreliable and error-prone, especially with inconsistent video quality or environmental noise.

---

## The Solution

Fanometer provides a *fun but impractical* way to “measure” fan speed by using motion detection inside a selected region of interest. It’s more of a computer vision demo than an actual tool you can trust for real measurements.

---

## Technical Details

### Technologies/Components Used

#### For Software:
- **Languages Used**: Python
- **Libraries Used**: OpenCV, NumPy, Math
- **Tools Used**: DroidCam for streaming phone camera feed to PC

#### For Hardware:
- A phone with DroidCam installed
- A computer capable of running Python + OpenCV
- A fan (any type)


### How It Works
1. Connect your phone's camera to your computer using **DroidCam** (Wi-Fi or USB).
2. The script processes the live video feed using **OpenCV**.
3. It applies **Farneback Optical Flow** to detect rotational motion in a circular region.
4. Calculates and displays the **estimated RPM** of the fan.


#### Demo



https://github.com/user-attachments/assets/4b8199c9-2a7e-44b0-80b5-c634a9384d03



https://github.com/user-attachments/assets/575d577d-731f-4960-9455-207977208525




### Screenshots

![WhatsApp Image 2025-08-09 at 18 45 59_e1d3f214](https://github.com/user-attachments/assets/b635214b-3182-4032-a772-7660a5954271)
![WhatsApp Image 2025-08-09 at 18 45 59_a0874822](https://github.com/user-attachments/assets/cd56767c-6218-4bfc-b37c-762bb279885f)

---

### Installation
1. **Clone this repository**:
   ```bash
   git clone https://github.com/poojasnair2428/Fanometer.git
   cd Fanometer
