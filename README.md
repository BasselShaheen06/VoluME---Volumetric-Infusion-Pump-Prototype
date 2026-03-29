# 💉 Smart Infusion Pump – Arduino × Python Integrated System

### Developed by

**Mohamed Badawy · Kareem Taha · Kareem Hassan · Omar Gamal · Ahmed Salem · Bassel Shaheen**

---

## 🚀 Project Overview

This project is a **hardware–software co-design** that mimics the essential functions of a **real-world intravenous (IV) infusion pump**, integrating **Arduino-based sensor control** with a **Python-based graphical interface (GUI)**.

Our goal was to **simulate realistic infusion pump behaviors**, including:

* **Fluid flow control**
* **Color-based fluid detection (blood leak monitoring)**
* **Flow rate monitoring**
* **Alarm management**
* **Battery simulation**
* **Manual & automatic pump modes**

We aimed to capture both **technical accuracy** and **user safety mechanisms**, just like real infusion systems used in hospitals — all in a **miniaturized educational prototype** suitable for microelectronics learning and medical device training.

---

## ⚙️ System Architecture

### 🔧 Arduino Layer — “The Controller”

The Arduino Uno handles **sensor readings**, **pump actuation** (using Keypad Controls), and **alarm triggers**.

Key components:

* **Flowmeter (YF-S401)** → Measures real-time fluid flow rate
* **Color Sensor (TCS230/TCS3200)** → Detects abnormal fluid color (e.g., blood leakage)
* **2N2222 transistor circuit** → Controls the infusion pump speed
* **Buzzer** → Audible alarms for alerts and safety breaches

### 🧠 Python Layer — “The Interface & Intelligence”

Using **PyQt5**, the GUI acts as a digital display unit and control dashboard:

* Shows **real-time flow rate**, **pump power**, and **status indicators**
* Visual and auditory alarms (e.g., blood leakage, occlusion, low battery)
* Manual control slider for pump power
* Auto mode switch that lets Arduino handle safety logic
* Simulated **battery drain system** for embedded realism

Communication between both layers occurs through **Serial (USB)** using `pyserial`.

---

## 🖥️ How It Works

| Function                       | Description                                                                                                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🩸 **Blood Leakage Detection** | The color sensor identifies changes in the color spectrum of the fluid. If red intensity dominates, the system labels it as **BLOOD LEAKAGE** and immediately triggers an alarm. |
| 💧 **Flow Monitoring**         | The flowmeter sends pulse counts per second to measure **flow rate (mL/min)**. Low readings under normal power levels activate **occlusion warnings**.                           |
| ⚡ **Pump Control**             | The pump operates under either **AUTO** (sensor-based) or **MANUAL** (user-defined PWM speed) mode.                                                                              |
| 🔔 **Alarm System**            | Multi-tier alarms for blood leakage, occlusion, communication errors, and low battery — each with distinct sound and visual patterns.                                            |

---

## 🧩 Hardware Components

| Component                          | Function                                                  |
| ---------------------------------- | --------------------------------------------------------- |
| Arduino Uno 3                      | Core microcontroller for sensor & motor control           |
| YF-S401 Flowmeter                  | Measures flow rate of IV fluid                            |
| TCS230/TCS3200 Color Sensor        | Detects color changes (used for blood leakage simulation) |
| DC Pump + 2N2222 Transistor Driver | Simulates the infusion mechanism                          |
| Buzzer                             | Audible alarm feedback                                    |
| USB Serial Interface               | Communication bridge with Python GUI                      |

---

## 🖌️ Software Features

### Python GUI Highlights

* Built using **PyQt5**
* Real-time dashboard with large flow rate display
* Mode switching and pump power slider
* Dynamic alarm notifications with audio and visual cues
* Battery simulation and charge-level visualization
* Serial auto-detection for Arduino connection

### Arduino Code Highlights

* Interrupt-driven pulse counting for accurate flow rate
* Adaptive PWM pump control
* Automatic vs manual operating modes
* Real-time sensor calibration mapping
* Serial feedback protocol for GUI communication

---

## Why This Project Matters

This project merges **biomedical device logic** with **embedded systems design**, representing a miniature model of how **real infusion systems** handle safety-critical operations.

It was developed as part of a **Microelectronics internship initiative**, where our goal was to **bridge hardware reliability with software intelligence** — creating a tangible example of **medical technology engineering in practice**.

Working on this project helped us explore:

* Sensor calibration and signal interpretation
* Embedded real-time safety systems
* GUI–hardware integration through serial communication
* Human–machine interface design principles
* Cross-disciplinary collaboration between electronics and biomedical logic

---

## 🧩 Future Improvements

We envision extending this system with:

* IoT integration for remote monitoring
* Machine learning model for fluid type classification
* Touchscreen interface for hospital-style controls
* Real battery and power management circuitry
* 3D-printed enclosure mimicking a real IV pump front panel

---

## Getting Started

### Requirements

* **Arduino IDE** (for uploading `.ino` code)
* **Python 3.8+**
* Libraries:

  ```bash
  pip install pyqt5 pyserial playsound
  ```

  *(Optional: `qt_material` for themes)*

### Run Steps

1. Upload the Arduino sketch to your board.
2. Connect Arduino via USB.
3. Run the Python GUI:

   ```bash
   python infusion_pump_gui.py
   ```
4. Choose between **AUTO** and **MANUAL** modes.
5. Watch real-time flow, alarms, and battery updates!

---

## Team Members Contribution:---

[Mohamed Badawy](https://github.com/MohamedBadawy19)  
[Kareem Taha](https://github.com/Kareem-Taha-05)  
[Karim Hassan](https://github.com/karimhassan-808)  
[Omar Gamal](https://github.com/OmarGamalH)  
[Ahmed Salem](https://github.com/Ahmedo0oSalem)  
[Bassel Shaheen](https://github.com/BasselShaheen06)
