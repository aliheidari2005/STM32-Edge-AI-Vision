# 🧠 STM32 Edge AI: Real-Time Hand-Written Digit Recognition

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MicroPython](https://img.shields.io/badge/MicroPython-Ready-green)
![EdgeAI](https://img.shields.io/badge/Edge%20AI-Optimized-orange)
![Hardware](https://img.shields.io/badge/Hardware-STM32-lightgrey)

A lightweight, highly optimized Edge AI project that performs **real-time digit recognition (0-9)** directly on an STM32 microcontroller. 

Designed specifically for microcontrollers with extreme hardware constraints (e.g., **only 192 KB of RAM**), this project avoids heavy Deep Learning models that would crash the device. Instead, it uses **K-Means Clustering** to extract binary templates and ultra-fast **Bitwise Operations (Hamming Distance)** for pattern matching.

## ✨ Key Features
* **Zero Neural Network Overhead:** Achieves digit recognition without TensorFlow Lite or heavy, memory-consuming libraries.
* **Extreme RAM Optimization (192 KB Limits):** Images are scaled to `16x16` pixels and packed into four 64-bit integers. The MCU uses only **256 bytes** of RAM per frame, completely avoiding `MemoryError` crashes on 192 KB systems.
* **Ultra-Fast Matching:** Uses hardware-level `XOR` bitwise operations to calculate the Hamming Distance.
* **Real-Time Pipeline:** Laptop webcam captures the frame -> converts to 16x16 -> sends via USB Serial -> STM32 processes and displays the result on an OLED screen.

---

## 🛠️ Hardware Requirements
* **Microcontroller:** STM32 Board (running MicroPython) with ~192 KB RAM
* **Display:** 128x32 I2C OLED Display
* **Host Machine:** PC/Laptop with a Webcam
* **Connection:** Micro-USB / USB-C data cable

## 💻 Software & Libraries
* **Host PC:** `Python 3.x`, `OpenCV`, `scikit-learn`, `pyserial`, `numpy`
* **Microcontroller:** `MicroPython`, `machine (SoftI2C)`, `pyb (USB_VCP)`

---

## 📂 Project Structure
* `train_model.ipynb` (or `.py`) : Trains the model using the MNIST dataset, applies K-Means to find common writing styles per digit, and outputs the final `DIGIT_TEMPLATES` dictionary in 64-bit hex format within a dedicated cell.
* `webcam_sender.py` : Captures webcam feed on the PC, isolates the digit, resizes it to 16x16, and sends exactly 256 bytes over USB Serial.
* `receive_and_detect.py` : The core MicroPython script running on the STM32. It reads the USB buffer, calculates the Hamming Distance against the injected templates, and outputs the prediction to the OLED.

---

## 🚀 How It Works (The Edge AI Magic)
1. **Training Phase (PC):** We use K-Means to cluster the MNIST dataset into representative templates (e.g., 12 distinct writing styles) per digit. The output is directly generated as a Python dictionary.
2. **Bit-Packing:** A 16x16 binary image contains 256 pixels. We pack these 256 bits into exactly **four 64-bit integers**.
3. **Inference (MCU):** When the MCU receives a new 256-byte image from the webcam, it packs it into four 64-bit variables and runs an `XOR` operation against the stored templates. The template with the lowest bit difference (Hamming Distance) wins!

---

## ⚙️ Getting Started

**Step 1: Train the Model**
Run `train_model.ipynb` on your computer. At the end of the script, copy the generated `DIGIT_TEMPLATES` dictionary from the console/cell output.

**Step 2: Flash the MCU**
Paste the copied dictionary directly into the designated section inside `receive_and_detect.py`. Then, upload this script as your `main.py` onto the STM32 board.

**Step 3: Start the Vision Pipeline**
Ensure your STM32 is connected via USB. Run `webcam_sender.py` on your PC. Click on the webcam window, show a written digit to the camera, and press **`s`** on your keyboard to send the frame to the MCU!

---

## 🔮 Future Improvements
- [ ] **Dynamic Cluster Optimization (K-Tuning):** Implement a validation phase to dynamically find the optimal number of clusters (templates) for each specific digit to prevent overfitting, rather than using a fixed number (e.g., 12).
- [ ] **Threshold Calibration:** Add an adaptive or auto-calibrating threshold mechanism for image binarization to improve robustness under different lighting conditions.
- [ ] **Higher Resolution Support:** Explore support for 20x20 resolution while maintaining memory safety.
- [ ] **Direct MCU Camera Integration:** Implement automatic bounding-box detection directly on the MCU using an OV7670 camera module (eliminating the PC host).

---
*Created as a demonstration of highly efficient Embedded Machine Learning (TinyML) on constrained devices.*
