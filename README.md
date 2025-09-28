# ESP32 Sumobot Project - Bluetooth Controlled Robot

[![ESP32](https://img.shields.io/badge/ESP32-Development%20Board-blue)](https://www.espressif.com/en/products/socs/esp32)
[![Python](https://img.shields.io/badge/Python-3.7+-green)](https://python.org)
[![Arduino](https://img.shields.io/badge/Arduino-IDE-orange)](https://www.arduino.cc/en/software)
[![Bluetooth](https://img.shields.io/badge/Bluetooth-Classic-blue)](https://www.bluetooth.com/)

## 🎯 Project Overview

This project demonstrates the creation of a **Bluetooth-controlled sumobot** using ESP32 microcontroller, PS5 DualSense controller, and BTS7960 motor drivers. The robot can be controlled wirelessly from a Windows laptop using a custom dashboard application.

> **🎓 Educational Value**: This project showcases practical application of embedded systems, wireless communication, and user interface design in robotics applications.

## 🏆 Learning Objectives

- **🔧 ESP32 Programming**: Bluetooth communication, GPIO control, motor interfacing
- **⚙️ Motor Control**: BTS7960 driver implementation, differential drive logic
- **📡 Wireless Communication**: Bluetooth Classic protocol, serial communication
- **🖥️ User Interface**: Python dashboard with real-time control visualization
- **🔗 System Integration**: Hardware-software integration, debugging techniques

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

### Control Interface
| Component | Type | Communication |
|-----------|------|---------------|
| **Controller** | PS5 DualSense Wireless | Bluetooth Classic |
| **Dashboard** | Windows Python Application | Serial Communication |
| **Microcontroller** | ESP32 | Built-in Bluetooth |

## 📋 Pin Configuration

### ESP32 to BTS7960 Motor Driver
```
ESP32 Pin    →    BTS7960 Pin    →    Function
GPIO 17      →    Left RPWM      →    Left Motor Forward
GPIO 18      →    Left LPWM      →    Left Motor Backward
GPIO 19      →    Right RPWM     →    Right Motor Forward
GPIO 21      →    Right LPWM     →    Right Motor Backward
5V           →    Enable Pins    →    Motor Enable (tied to 5V)
GND          →    GND            →    Common Ground
```

### Power Distribution
```
Battery (7.4V-12V)
├── ESP32 VIN (5V input via voltage regulator)
├── BTS7960 Motor Power (direct battery voltage)
└── Common Ground (all components)
```

## 🔧 Software Architecture

### ESP32 Code (`esp32-test.ino`)
- **Bluetooth Communication**: Receives commands from Windows dashboard
- **Motor Control**: Direct GPIO control of BTS7960 drivers
- **Protocol Parsing**: Interprets PS5 controller data
- **LED Indicators**: Visual feedback for motor control debugging

### Windows Dashboard (`BT_Dashboard.py`)
- **Controller Input**: PS5 DualSense via pygame library
- **Real-time Visualization**: Motor speed bars, movement indicators
- **Bluetooth Communication**: Serial communication to ESP32
- **Auto-detection**: Automatic ESP32 COM port detection

## 📡 Communication Protocol

### Data Format
```cpp
F <throttle> <turn> <brake> <rotate> <gear_boost>
```

### Parameters
| Parameter | Range | Description |
|-----------|-------|-------------|
| **throttle** | -1.0 to 1.0 | Forward/backward movement |
| **turn** | -1.0 to 1.0 | Left/right steering |
| **brake** | 0 or 1 | Emergency stop |
| **rotate** | 0 or 1 | Spin in place |
| **gear_boost** | 0 or 1 | Speed multiplier |

### Example Commands
```cpp
F 0.500 0.000 0 0 0    // Forward at 50% speed
F 0.000 0.300 0 0 0    // Turn right
F 0.000 0.000 1 0 0    // Emergency brake
F 0.000 0.000 0 1 0    // Rotate in place
F 0.800 0.000 0 0 1    // Forward with boost
```

## 🎮 Control Mapping

### PS5 DualSense Controller
| Input | Function | Description |
|-------|----------|-------------|
| **Left Stick (Y-axis)** | Throttle | Forward/backward movement |
| **Left Stick (X-axis)** | Turn | Left/right steering |
| **R2 Trigger** | Brake | Emergency stop |
| **X Button** | Rotate | Spin in place |
| **Square Button** | Gear Boost | Speed increase |

### Keyboard Controls (Fallback)
| Key | Function | Description |
|-----|----------|-------------|
| **W/S** | Throttle | Forward/backward |
| **A/D** | Turn | Left/right |
| **B** | Brake | Emergency stop |
| **X** | Rotate | Spin in place |
| **Space** | Deadman | Safety switch |

## 🚀 Setup Instructions

### 1. Hardware Assembly

#### ESP32 to BTS7960 Connections
```bash
GPIO 17 → Left RPWM
GPIO 18 → Left LPWM
GPIO 19 → Right RPWM
GPIO 21 → Right LPWM
5V → Enable pins (tied to 5V)
GND → Common ground
```

#### Motor Connections
```bash
Left motor → BTS7960 OUT1, OUT2
Right motor → BTS7960 OUT3, OUT4
Motor power → Battery (7.4V-12V)
```

#### Power Supply
```bash
ESP32 VIN → 5V source
BTS7960 VCC → Battery
Common ground → All components
```

### 2. Software Installation

#### ESP32 Setup
1. **Install Arduino IDE**
2. **Add ESP32 Board Package**:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. **Install ESP32 Board**: Tools → Board Manager → Search "ESP32" → Install
4. **Select Board**: "ESP32 Dev Module"

#### Windows Dashboard Setup
```bash
# Install Python dependencies
pip install pygame pyserial tkinter

# Download project files
git clone <repository-url>
cd sumobot
```

### 3. Programming and Testing

#### ESP32 Programming
1. **Upload Code**:
   - Open `esp32-test.ino` in Arduino IDE
   - Select correct COM port
   - Upload to ESP32

2. **Test Motors**:
   - Open Serial Monitor (115200 baud)
   - Watch for "Motor Test: Forward for 2 seconds..."
   - Verify motors move during test

#### Bluetooth Pairing
1. **Enable ESP32 Bluetooth**:
   - ESP32 broadcasts as "ESP32-Sumobot"
   - Wait for "Bluetooth device started" message

2. **Windows Pairing**:
   - Settings → Devices → Bluetooth & other devices
   - Add device → Bluetooth
   - Select "ESP32-Sumobot"
   - Create COM port (Outgoing)

#### Dashboard Testing
```bash
# Run dashboard
python BT_Dashboard.py --com COMx --dashboard

# Test controller
# Connect PS5 controller via Bluetooth
# Move left stick to control robot
# Press buttons for special functions
```

## 🔍 Troubleshooting

### Common Issues

#### Bluetooth Connection
| Error | Cause | Solution |
|-------|-------|---------|
| **"Could not open port"** | Wrong COM port or already in use | Check Device Manager, close other apps |
| **"Semaphore timeout"** | Port in use | Close Serial Monitor, try different COM port |
| **"Access denied"** | Another app using port | Close all serial applications |

#### Motor Issues
| Problem | Cause | Solution |
|--------|-------|---------|
| **Motors not moving** | Insufficient power | Check power supply (7.4V-12V) |
| **Wrong direction** | Incorrect wiring | Swap motor wires on BTS7960 |
| **Noisy operation** | Electrical interference | Add capacitors (100µF) across motor terminals |

#### ESP32 Issues
| Problem | Cause | Solution |
|--------|-------|---------|
| **Upload fails** | Boot mode not entered | Hold BOOT button during upload |
| **Bluetooth not found** | Device name mismatch | Check device name in code |
| **Random resets** | Power instability | Check power supply stability |

### Debugging Steps
1. **Check Serial Monitor** for error messages
2. **Verify all connections** with multimeter
3. **Test with `esp32-debug.ino`** for GPIO functionality
4. **Check Windows Device Manager** for COM ports
5. **Ensure proper power supply voltage**

## 📊 Performance Metrics

### System Performance
| Metric | Value | Notes |
|--------|-------|-------|
| **Latency** | ~5-10ms | Extremely responsive |
| **Bluetooth Range** | 10-30 meters | Depends on environment |
| **Motor Speed** | 0-100% | Smooth control |
| **Battery Life** | 30-60 minutes | Depends on usage |

### Control Features
- **🔄 Differential Drive**: Independent left/right motor control
- **⚡ Speed Control**: Variable speed based on stick position
- **🛑 Special Functions**: Brake, rotate, gear boost
- **📊 Real-time Feedback**: LED indicators and dashboard visualization

## 🎓 Learning Outcomes

### Technical Skills Developed
- **🔧 Microcontroller Programming**: ESP32 development and debugging
- **⚙️ Motor Control Systems**: H-bridge drivers and PWM control
- **📡 Wireless Communication**: Bluetooth protocol implementation
- **🖥️ User Interface Design**: Python GUI development
- **🔗 System Integration**: Hardware-software coordination

### Problem-Solving Skills
- **🐛 Debugging Techniques**: Serial monitoring, LED indicators
- **🔧 Hardware Troubleshooting**: Connection verification, power analysis
- **⚡ Software Optimization**: Latency reduction, performance tuning
- **📚 Documentation**: Code commenting, README creation

## 🔮 Future Enhancements

### Hardware Improvements
- **📡 Sensors**: Ultrasonic (HC-SR04), IMU (MPU6050), line sensors
- **🔋 Power Management**: Battery monitoring, low voltage protection
- **🛡️ Safety Features**: Physical kill switch, current limiting

### Software Features
- **🌐 WiFi Dashboard**: Web-based control interface
- **📊 Data Logging**: Movement recording and analysis
- **🤖 Autonomous Mode**: Line following, obstacle avoidance
- **📱 Mobile App**: Android/iOS control application

## 📁 Project Files

```
sumobot/
├── esp32-test.ino          # ESP32 main code
├── BT_Dashboard.py         # Windows dashboard
├── README.md               # This documentation
└── docs/                   # Additional documentation
    ├── wiring_diagram.png  # Hardware connections
    ├── pinout_guide.pdf    # ESP32 pin reference
    └── troubleshooting.md  # Common issues and solutions
```

## 👥 Team Members

- **🔧 Hardware Design**: ESP32 integration, motor driver selection
- **💻 Software Development**: Bluetooth communication, dashboard UI
- **🧪 Testing & Debugging**: System integration, performance optimization
- **📚 Documentation**: README creation, troubleshooting guide

## 📚 References

- **ESP32 Documentation**: https://docs.espressif.com/projects/esp-idf/
- **BTS7960 Datasheet**: Motor driver specifications
- **Python Libraries**: pygame, pyserial, tkinter documentation
- **Arduino IDE**: ESP32 board package installation

## 🏆 Project Success Criteria

✅ **ESP32 Programming**: Successfully programmed and tested  
✅ **Motor Control**: Both motors respond to PS5 input  
✅ **Bluetooth Communication**: Reliable wireless control  
✅ **Dashboard Interface**: Real-time visualization working  
✅ **System Integration**: All components working together  
✅ **Documentation**: Comprehensive project documentation  

---

**This project demonstrates practical application of embedded systems, wireless communication, and user interface design in robotics applications.**
