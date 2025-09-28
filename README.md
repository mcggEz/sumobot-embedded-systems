# ESP32 Sumobot Project - Bluetooth Controlled Robot

## 🎯 Project Overview

This project demonstrates the creation of a **Bluetooth-controlled sumobot** using ESP32 microcontroller, PS5 DualSense controller, and BTS7960 motor drivers. The robot can be controlled wirelessly from a Windows laptop using a custom dashboard application.

## 🏆 Learning Objectives

- **ESP32 Programming**: Bluetooth communication, GPIO control, motor interfacing
- **Motor Control**: BTS7960 driver implementation, differential drive logic
- **Wireless Communication**: Bluetooth Classic protocol, serial communication
- **User Interface**: Python dashboard with real-time control visualization
- **System Integration**: Hardware-software integration, debugging techniques

## 🛠️ Hardware Components

### Main Controller
- **ESP32 Development Board** (ESP32-WROOM-32)
- **Power**: 5V input via VIN pin
- **GPIO**: 34 digital pins available
- **Built-in Features**: WiFi, Bluetooth Classic, ADC, PWM

### Motor Control System
- **Motors**: 2x DC Motors (6V-12V, 200-500 RPM)
- **Motor Driver**: BTS7960 Dual H-Bridge Motor Driver
- **Power Supply**: 7.4V-12V LiPo battery or 9V battery pack
- **Current Capacity**: Up to 43A per channel

### Control Interface
- **Controller**: PS5 DualSense Wireless Controller
- **Communication**: Bluetooth Classic (built-in ESP32)
- **Dashboard**: Windows Python application with real-time visualization

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
```
F <throttle> <turn> <brake> <rotate> <gear_boost>
```

### Parameters
- **throttle**: -1.0 to 1.0 (forward/backward movement)
- **turn**: -1.0 to 1.0 (left/right steering)
- **brake**: 0 or 1 (emergency stop)
- **rotate**: 0 or 1 (spin in place)
- **gear_boost**: 0 or 1 (speed multiplier)

### Example Commands
```
F 0.500 0.000 0 0 0    # Forward at 50% speed
F 0.000 0.300 0 0 0    # Turn right
F 0.000 0.000 1 0 0    # Emergency brake
F 0.000 0.000 0 1 0    # Rotate in place
F 0.800 0.000 0 0 1    # Forward with boost
```

## 🎮 Control Mapping

### PS5 DualSense Controller
- **Left Stick (Y-axis)**: Throttle control (forward/backward)
- **Left Stick (X-axis)**: Turn control (left/right)
- **R2 Trigger**: Brake (emergency stop)
- **X Button**: Rotate (spin in place)
- **Square Button**: Gear boost (speed increase)

### Keyboard Controls (Fallback)
- **W/S**: Throttle (forward/backward)
- **A/D**: Turn (left/right)
- **B**: Brake
- **X**: Rotate
- **Space**: Deadman switch

## 🚀 Setup Instructions

### 1. Hardware Assembly
1. **Connect ESP32 to BTS7960**:
   - GPIO 17 → Left RPWM
   - GPIO 18 → Left LPWM
   - GPIO 19 → Right RPWM
   - GPIO 21 → Right LPWM
   - 5V → Enable pins (tied to 5V)
   - GND → Common ground

2. **Connect Motors**:
   - Left motor to BTS7960 OUT1, OUT2
   - Right motor to BTS7960 OUT3, OUT4
   - Motor power from battery (7.4V-12V)

3. **Power Supply**:
   - ESP32 VIN from 5V source
   - BTS7960 VCC from battery
   - Common ground connection

### 2. Software Installation

#### ESP32 Setup
1. **Install Arduino IDE**
2. **Add ESP32 Board Package**:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. **Install ESP32 Board**: Tools → Board Manager → Search "ESP32" → Install
4. **Select Board**: "ESP32 Dev Module"

#### Windows Dashboard Setup
1. **Install Python Dependencies**:
   ```bash
   pip install pygame pyserial tkinter
   ```
2. **Download Project Files**:
   - `esp32-test.ino` (ESP32 code)
   - `BT_Dashboard.py` (Windows dashboard)

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
1. **Run Dashboard**:
   ```bash
   python BT_Dashboard.py --com COMx --dashboard
   ```
   (Replace COMx with actual COM port)

2. **Test Controller**:
   - Connect PS5 controller via Bluetooth
   - Move left stick to control robot
   - Press buttons for special functions

## 🔍 Troubleshooting

### Common Issues

#### Bluetooth Connection
- **"Could not open port"**: Wrong COM port or already in use
- **"Semaphore timeout"**: Close Serial Monitor, try different COM port
- **"Access denied"**: Another app is using the port

#### Motor Issues
- **Motors not moving**: Check power supply (7.4V-12V)
- **Wrong direction**: Swap motor wires on BTS7960
- **Noisy operation**: Add capacitors (100µF) across motor terminals

#### ESP32 Issues
- **Upload fails**: Hold BOOT button during upload
- **Bluetooth not found**: Check device name in code
- **Random resets**: Check power supply stability

### Debugging Steps
1. **Check Serial Monitor** for error messages
2. **Verify all connections** with multimeter
3. **Test with `esp32-debug.ino`** for GPIO functionality
4. **Check Windows Device Manager** for COM ports
5. **Ensure proper power supply voltage**

## 📊 Performance Metrics

### System Performance
- **Latency**: ~5-10ms (extremely responsive)
- **Bluetooth Range**: 10-30 meters
- **Motor Speed**: 0-100% (smooth control)
- **Battery Life**: 30-60 minutes (depending on usage)

### Control Features
- **Differential Drive**: Independent left/right motor control
- **Speed Control**: Variable speed based on stick position
- **Special Functions**: Brake, rotate, gear boost
- **Real-time Feedback**: LED indicators and dashboard visualization

## 🎓 Learning Outcomes

### Technical Skills Developed
- **Microcontroller Programming**: ESP32 development and debugging
- **Motor Control Systems**: H-bridge drivers and PWM control
- **Wireless Communication**: Bluetooth protocol implementation
- **User Interface Design**: Python GUI development
- **System Integration**: Hardware-software coordination

### Problem-Solving Skills
- **Debugging Techniques**: Serial monitoring, LED indicators
- **Hardware Troubleshooting**: Connection verification, power analysis
- **Software Optimization**: Latency reduction, performance tuning
- **Documentation**: Code commenting, README creation

## 🔮 Future Enhancements

### Hardware Improvements
- **Sensors**: Ultrasonic (HC-SR04), IMU (MPU6050), line sensors
- **Power Management**: Battery monitoring, low voltage protection
- **Safety Features**: Physical kill switch, current limiting

### Software Features
- **WiFi Dashboard**: Web-based control interface
- **Data Logging**: Movement recording and analysis
- **Autonomous Mode**: Line following, obstacle avoidance
- **Mobile App**: Android/iOS control application

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

- **Hardware Design**: ESP32 integration, motor driver selection
- **Software Development**: Bluetooth communication, dashboard UI
- **Testing & Debugging**: System integration, performance optimization
- **Documentation**: README creation, troubleshooting guide

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
#   s u m o b o t - e m b e d d e d - s y s t e m s  
 