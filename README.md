# Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping

Official code repository for the paper:  
**"Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping"**

## Overview
This repository provides the control and communication code for the modular soft gripper system described in the paper.
The system integrates Arduino-based low-level actuation and a Python control interface for proprioceptive feedback and grasp modulation.

## Repository Structure
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

## Requirements
### Python Environment
- Python ≥ 3.8
- Install required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
### Arduino Environment
- Arduino IDE ≥ 2.0
- Required Libraries:
  1. [Adafruit LPS35HW Library](https://github.com/adafruit/Adafruit_LPS35HW) (Provides the   `Adafruit_LPS35HW.h` header used for pressure sensing)
  2. [Adafruit Sensor Library](https://github.com/adafruit/Adafruit_Sensor) (Dependency required by LPS35HW library)
  To install:
  1. Open **Arduino IDE**
  2. Go to **Tools → Manage Libraries...**
  3. Search for **“Adafruit LPS35HW”**
  4. Click **Install** (this will automatically install its dependencies)

## Usage
### Upload the Arduino Code
1. Open `Arduino/Gripper_FullCode.ino` in **Arduino IDE**
2. Ensure the **Adafruit_LPS35HW** and **Adafruit_Sensor** libraries are installed
3. Select the correct **Board** and **Port**
4. Click **Upload**

### Run the Python Control Interface
```bash
python Python/GripperControl.py --port COM4
```
This command launches the UI for controlling the gripper and visualizing proprioceptive (pressure-based) feedback. Make sure to replace `COM4` with the serial port corresponding to your Arduino Control Board. You can check the active serial port under **Tools → Port** in the **Arduino IDE**. If `--port ...` is omitted, the program will use the default port setting `COM4`.

## Authors
*Dong Heon Han¹, Xiaohao Xu², Yuxi Chen¹, Yusheng Zhou², Xinqi Zhang¹, Jiaqi Wang², Daniel Bruder¹, Xiaonan Huang²*  

¹ *Mechanical Engineering Department, University of Michigan – Ann Arbor, Ann Arbor, MI, USA* 
  - `{dongheon, ethansab, dadaaa, dbruder}@umich.edu`
    
² *Robotics Department, University of Michigan – Ann Arbor, Ann Arbor, MI, USA*
  - `{xiaohaox, yszhou, wangjq, xiaonanh}@umich.edu` 
