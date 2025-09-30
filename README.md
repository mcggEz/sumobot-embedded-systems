# ESP32 Sumobot Project - Bluetooth Controlled Robot

[![ESP32](https://img.shields.io/badge/ESP32-Development%20Board-blue)](https://www.espressif.com/en/products/socs/esp32)
[![Python](https://img.shields.io/badge/Python-3.7+-green)](https://python.org)
[![Arduino](https://img.shields.io/badge/Arduino-IDE-orange)](https://www.arduino.cc/en/software)
[![Bluetooth](https://img.shields.io/badge/Bluetooth-Classic-blue)](https://www.bluetooth.com/)

## 🎯 Project Overview

This project demonstrates the creation of a **Bluetooth-controlled sumobot** using ESP32 microcontroller, PS5 DualSense controller, and BTS7960 motor drivers. The robot can be controlled wirelessly using a PS5 controller.

## 🏆 Learning Objectives

- **🔧 ESP32 Programming**: Bluetooth communication, GPIO control, motor interfacing
- **⚙️ Motor Control**: BTS7960 driver implementation, differential drive logic
- **📡 Wireless Communication**: Bluetooth Classic protocol, serial communication


## 🛠️ Hardware Components

### Main Controller
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **ESP32 Development Board** | ESP32-WROOM-32 | Main microcontroller |
| **Power Input** | 5V via VIN pin | Power supply |
| **GPIO Pins** | 34 digital pins | Motor control, sensors |
| **Built-in Features** | WiFi, Bluetooth Classic, ADC, PWM | Communication & control |

### Motor Control System
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Motors** | 2x DC Motors (6V-12V, 200-500 RPM) | Robot movement |
| **Motor Driver** | BTS7960 Dual H-Bridge | Motor control |
| **Power Supply** | 7.4V-12V LiPo battery | System power |
| **Current Capacity** | Up to 43A per channel | High current handling |

## 🔧 Software Architecture

### ESP32 Code (`esp32-test.ino`)
- **Bluetooth Communication**: Receives commands from Windows dashboard
- **Motor Control**: Direct GPIO control of BTS7960 drivers
- **Protocol Parsing**: Interprets PS5 controller data

## 🎮 Control Mapping

### PS5 DualSense Controller
| Input | Function | Description |
|-------|----------|-------------|
| **Left Stick (Y-axis)** | Throttle | Forward/backward movement |
| **Left Stick (X-axis)** | Turn | Left/right steering |
| **R2 Trigger** | Brake | Emergency stop |
| **X Button** | Rotate | Spin in place |


### Control Features
- **🔄 Differential Drive**: Independent left/right motor control
- **⚡ Speed Control**: Variable speed based on stick position
- **🛑 Special Functions**: Brake, rotate, gear boost
- **📊 Real-time Feedback**: LED indicators and dashboard visualizatio

  <img width="362" height="226" alt="image" src="https://github.com/user-attachments/assets/cc01eaa5-60d4-41ec-82e5-adaeb9e69575" />
  <img width="426" height="241" alt="image" src="https://github.com/user-attachments/assets/f687ad96-a6cc-44ed-af2d-73bf1802bab2" />




**This project demonstrates the creation of a **Bluetooth-controlled sumobot** using ESP32 microcontroller, PS5 DualSense controller, and BTS7960 motor drivers. The robot can be controlled wirelessly using a PS5 controller.**
