# Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping

Official code repository for the paper:  
**"Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping"**

# Overview
This repository provides the control and communication code for the modular soft gripper system described in the paper.
The system integrates Arduino-based low-level actuation and a Python control interface for proprioceptive feedback and grasp modulation.

# Repository Structure
```bash
main/
├── Gripper_FullCode/
│   └── Gripper_FullCode.ino        # Firmware controlling the modular soft gripper
├── GripperControl.py               # Main Python UI and control logic
├── serial_controller.py            # Handles serial communication with Arduino
├── uipic.png                       # UI illustration
├── requirements.txt
└── README.md
```

# Requirements
## Python Environment
- Python ≥ 3.8
- Install required dependencies:
  ```bash
  pip install -r requirements.txt
## Arduino Environment
- Arduino IDE ≥ 2.0
- Required Libraries: [Adafruit PWM Servo Driver Library](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library) (Provides the Adafruit_PWMServoDriver.h header)
