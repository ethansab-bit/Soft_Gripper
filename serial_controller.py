import serial
import time

class SerialController:
    def __init__(self, port='COM4', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        print(f"Connected to {port} at {baudrate} baud")

    def sendActState(self, actState):
        assert len(actState) == 4
        msg = f"{actState[0]:.2f} {actState[1]:.2f} {actState[2]:.2f} {actState[3]:.2f}\n"
        self.ser.write(msg.encode())
        print("Send Actuator State: ", msg.strip())

    def sendFinState(self, finState):
        assert finState in ['G', 'R']
        msg = f"{finState}\n"
        self.ser.write(msg.encode())
        print("Sent Finger State: ", msg.strip())

    def readOutput(self):
        if self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                parts = line.split()

                if len(parts) == 12:
                    curPre = list(map(float, parts[:4]))
                    stopFlag = parts[4:8]
                    graspFlag = parts[8:12]
                    return curPre, stopFlag, graspFlag, None

                if len(parts) == 16:
                    curPre = list(map(float, parts[:4]))
                    stopFlag = parts[4:8]
                    graspFlag = parts[8:12]
                    bendVals = list(map(int, parts[12:16]))
                    return curPre, stopFlag, graspFlag, bendVals

            except Exception as e:
                print("[Serial Parse Error]", e)
        return None, None, None, None



    def close(self):
        self.ser.close()

        print("Serial connection closed.")
