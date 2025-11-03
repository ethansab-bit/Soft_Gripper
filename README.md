
# Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping

Official code repository for the paper:  
**"Whole-Body Proprioceptive Morphing: A Modular Soft Gripper for Robust Cross-Scale Grasping"**

## Authors

**Dong Heon Han¹, Xiaohao Xu²†, Yuxi Chen¹, Yusheng Zhou², Xinqi Zhang¹, Jiaqi Wang², Daniel Bruder¹, Xiaonan Huang²***  

¹ *Mechanical Engineering Department, University of Michigan – Ann Arbor, Ann Arbor, MI, USA*  
² *Robotics Department, University of Michigan – Ann Arbor, Ann Arbor, MI, USA*  

† *Project Lead* | * Corresponding Author  

**Emails:**  
- (dongheon, ethansab, dadaaa, dbruder)@umich.edu
- (xiaohaox, yszhou, wangjq, xiaonanh)@umich.edu

![12](https://github.com/user-attachments/assets/5df8fcfc-32cf-449a-ac50-b75a1592e3c3)

## Overview
This repository provides the control and communication code for the modular soft gripper system described in the paper.
The system integrates Arduino-based low-level actuation and a Python control interface for proprioceptive feedback and grasp modulation.

## Repository Structure
```bash
main/
├── Gripper_CAD/                    # CAD files
├── Gripper_FullCode/
│   └── Gripper_FullCode.ino        # Firmware controlling the modular soft gripper
├── GripperControl.py               # Main Python UI and control logic
├── serial_controller.py            # Handles serial communication with Arduino
├── uipic.png                       # UI illustration
├── UserInterfaceDemo.png
├── Schematic_Gripper.png
├── requirements.txt
└── README.md
```

## Clone the Repository
To download or clone this repository:
### Option 1 — Using HTTPS
```bash
git clone https://github.com/ethansab-bit/Soft_Gripper.git
```
### Option 2 — Download ZIP
Click the **Code → Download ZIP** button on GitHub, then unzip the project folder locally.

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
### System Wiring
The control system requires the following electric devices:
  - Arduino Mega2560 Control Board × 1
  - L298N Motor Driver × 3
  - X605LF Valve × 10
  - LPS3X Pressure Sensor × 4
  - Bending Sensor × 4

The **Arduino Mega2560** should remain connected to the computer **at all times** for communication and control.
All **L298N motor drivers** and bending sensors must be powered by a **5 V** source.

Each bending sensor should be connected in series with a **15 kΩ resistor** to ground. The junction point between the sensor and the resistor should be wired to one of the **analog input ports (A0–A15)** on the Mega2560.

All **VCC pins** of the LPS3X pressure sensors should be connected to the **3.3 V output** on the Mega2560.

The complete wiring layout is illustrated in the diagram below:
<p align="center">
  <img src="Schematic_Gripper.png" width="600">
</p>

### Upload the Arduino Code
1. Open `Gripper_FullCode/Gripper_FullCode.ino` in **Arduino IDE**
2. Ensure the **Adafruit_LPS35HW** and **Adafruit_Sensor** libraries are installed
3. Select the correct **Board** and **Port**
4. Click **Upload**

**Notice**: The `Gripper_FullCode.ino` file **must remain inside its folder with the same name** (`Gripper_FullCode/`). Otherwise, the Arduino IDE will not be able to locate dependencies and compile the code.

### Run the Python Control Interface
```bash
python GripperControl.py --port COM4
```
This command launches the UI for controlling the gripper and visualizing proprioceptive (pressure-based) feedback. Make sure to **replace** `COM4` **with the serial port corresponding to your Arduino Control Board**. You can check the active serial port under **Tools → Port** in the **Arduino IDE**. If `--port ...` is omitted, the program will use the default port setting `COM4`.

**Notice**: Before running the Python control program, make sure to **close the Serial Monitor** in the Arduino IDE (or any other application accessing the serial port). **Only one program can use the serial connection at a time**.

### Control Interface Operation
The graphical user interface (GUI) allows users to control and monitor each pneumatic actuator of the soft gripper in real time.  
Each actuator’s target and measured pressure (in hPa) are displayed along with control sliders and state indicators.
<p align="center">
  <img src="UserInterfaceDemo.png" width="600">
</p>
Users can:

  - Adjust actuator length using the on-screen sliders (0.00-1.00 extension)
  - Observe real-time sensor readings from **LPS35HW** pressure sensors  
  - Control the gripper finger states (`Finger State` button, `R` for **Release**, `G` for **Gripped**)  
  - Log the data from four bending sensors (`Log BS`). The data will be stored in the same directory as `bend_log.txt`.
  - Recalibrate the actuator (`Restart`). The system will release all air pressure in actuators and fingers and automatically recalibrate to atmospheric pressure within a few seconds.

## CAD Files
All CAD resources for the soft gripper are organized within the repository: Soft_Gripper / Gripper_CAD

## Paper
arxiv: https://arxiv.org/abs/2510.27666

---

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
