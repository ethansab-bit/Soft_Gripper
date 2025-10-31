#include <Adafruit_LPS35HW.h>
#include <SPI.h>
#include <math.h>

// Port Declaration
#define SCK 52
#define SDO 50
#define SDI 51
const int CSP[4] = {6, 7, 8, 9};

const int BS[4] = {A2, A3, A0, A1};

const int ActIn[4]  = {22, 24, 26, 28};
const int ActOut[4] = {23, 25, 27, 29};

const int FinIn = 2;
const int FinOut = 3;

// Pressure Sensor
Adafruit_LPS35HW preSensor[4] = {Adafruit_LPS35HW(), Adafruit_LPS35HW(), Adafruit_LPS35HW(), Adafruit_LPS35HW()};

// Time Variable
unsigned long curTime;
unsigned long preTime;
float dt = 0;
float cycleLength = 100;
unsigned long startCycle = 0;
const int finChargeCycle = 10;
const float finChargeProp = 0.5;

// Pressure Variable
float targetPre[4] = {0, 0, 0, 0};
float currentPre[4] = {0, 0 ,0 ,0};
float errorPre[4] = {0, 0, 0, 0};
float atmPre = 0;

// Input Variable
float targetActState[4] = {0, 0, 0, 0};
bool targetFinState = false;

// Output Variable
int gripFlag[4] = {0, 0, 0, 0};
bool stopFlag[4] = {true, true, true, true};
const int gripRange[4] = {82, 46, 47, 23};
const int gripLowLimit[4] = {91, 29, 119, 47};
const float gripThrehold[4] = {.95, .60, .60, .90};

// PID Constant
const float Kp = 0.001;
const float Ki = 0.000003;
const float Kd = 0.000008;

// Control Constant
const float deadLimit = 0.03;
float interval = 1076.0230;

// PID Variable
float integral[4] = {0, 0, 0, 0};
float derivative[4] ={0, 0, 0, 0};
float error[4] = {0, 0, 0, 0};
float preError[4] = {0, 0, 0, 0};
float score[4] = {0, 0, 0, 0};

// Function Declaration
void ReadInput();
void InitialState();
void Len2Pre();
void readCurPre();
void CalcTime();
void CalcPID();
void ControlValve();
void PrintInfo();

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 

  // Initiate Pressure Sensor
  for (int i = 0; i < 4; i++) {
    if (!preSensor[i].begin_SPI(CSP[i], SCK, SDO, SDI)) {
      Serial.print("Invalid Pressure Sensor #");
      Serial.println(i);
      while(1);
    }
  }

  // Initaite the Valve
  for (int i = 0; i < 4; i++) {
    pinMode(ActIn[i], OUTPUT);
    pinMode(ActOut[i], OUTPUT);
  }
  pinMode(FinIn, OUTPUT);
  pinMode(FinOut, OUTPUT);

  // Initiate Time
  curTime = millis();
  preTime = millis();

  InitialState();
}


void loop() {
  // put your main code here, to run repeatedly:
  ReadInput();
  Len2Pre();
  readCurPre();
  readGripFlag();
  CalcTime();
  CalcPID();
  ControlValve();
  PrintInfo();
}

void ReadInput() {
  // Read input from the serial, changing length by "l1 l2 l3 l4", constrol finger by "G" or "R", restart by "S"
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input == "s" || input == "S") {
      for (int i = 0; i < 4; i++) {
        targetActState[i] = 0;
      }
      targetFinState = false;
      InitialState();
      return;
    }

    if (input == "g" || input == "G") {
      targetFinState = true;
    } else if (input == "r" || input == "R") {
      targetFinState = false;
    }

    float temp[4];
    int index = 0;

    int lastSpace = -1;
    for (int i = 0; i < input.length(); i++) {
      if (input.charAt(i) == ' ' || i == input.length() - 1) {
        int endIdx = (input.charAt(i) == ' ') ? i : i + 1;
        String numStr = input.substring(lastSpace + 1, endIdx);
        numStr.trim();
        if (index < 4) {
          temp[index] = numStr.toFloat();
          index++;
        }
        lastSpace = i;
      }
    }

    if (index == 4) {
      for (int i = 0; i < 4; i++) {
        targetActState[i] = constrain(temp[i], 0.0, 1.2);
      }
    } else {
      Serial.println("Invalid input. Please enter 4 numbers.");
    }
  }
}

void InitialState() {
  // Release all the pressure in fingers & actuators
  for (int i = 0; i < 4; i++) {
    digitalWrite(ActIn[i], LOW);
    digitalWrite(ActOut[i], HIGH);
    delay(1000);
  }
  digitalWrite(FinIn, LOW);
  digitalWrite(FinOut, HIGH);
  delay(1000);

  // Measure & Reset the atmosphere pressure
  float sumPre = 0;
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 10; j++) {
      sumPre += preSensor[i].readPressure();
    }
  }
  atmPre = sumPre / 40;
  delay(500);
}

void Len2Pre() {
  // Transfer the length proportion into pressure
  
  for (int i = 0; i < 4; i++) {
    if (targetActState[i] == 0) {
      targetPre[i] = 0;
      continue;
    }
    float targetLength = 70 * (1 + targetActState[i]);
    targetPre[i] = 0.002 * targetLength * targetLength * targetLength - 0.6508 * targetLength * targetLength + 75.6529 * targetLength - 1798.7 - atmPre;
  }
}

void readCurPre() {
  for (int i = 0; i < 4; i++) {
    currentPre[i] = preSensor[i].readPressure() - atmPre;
  }
}

void readGripFlag() {
  if (targetFinState) {
    for (int i = 0; i < 4; i++) {
      if ((float)(analogRead(BS[i]) - gripLowLimit[i])/(float)gripRange[i] < gripThrehold[i]) {
        gripFlag[i] = 1;
      } else {
        gripFlag[i] = -1;
      }
    }
  } else {
    for (int i = 0; i < 4; i++) {
      gripFlag[i] = 0;
    }
  }
}

void CalcTime() {
  // Calculate the derivative time and renew curTime & preTime
  curTime = millis();
  dt = (curTime - preTime) / 1000.0;
  preTime = curTime;
}

void CalcPID() {
  // Calculate PID with constant and variable and return a estimate score from -1 to 1
  for (int i = 0; i < 4; i++) {
    error[i] = targetPre[i] - currentPre[i];
    integral[i] += error[i] * dt;
    derivative[i] = (error[i] - preError[i]) / dt;
    preError[i] = error[i];
    score[i] = constrain(Kp * error[i] + Ki * integral[i] + Kd * derivative[i], -1, 1);
  }
}

void ControlValve() {
  // Control the actuators and fingers using the PID control variables
  unsigned long curTimeTemp = millis();
  unsigned long curCycleTime = curTimeTemp - startCycle;

  if (curCycleTime >= cycleLength) {
    startCycle = curTimeTemp;
    curCycleTime = 0;
  }

  for (int i = 0; i < 4; i++) {
    if (score[i] > deadLimit && curCycleTime < fabs(score[i]) * cycleLength) {
      digitalWrite(ActIn[i], HIGH);
      digitalWrite(ActOut[i], LOW);
      stopFlag[i] = false;
    } else if (score[i] < -deadLimit && curCycleTime < fabs(score[i]) * cycleLength) {
      digitalWrite(ActIn[i], LOW);
      digitalWrite(ActOut[i], HIGH);
      stopFlag[i] = false;
    } else {
      digitalWrite(ActIn[i], LOW);
      digitalWrite(ActOut[i], LOW);
      if (score[i] >= -deadLimit && score[i] <= deadLimit) {
        integral[i] = 0;
        stopFlag[i] = true;
      }
    }
  }

  if (targetFinState) {
    digitalWrite(FinIn, HIGH);
    digitalWrite(FinOut, LOW);
  } else {
    digitalWrite(FinIn, LOW);
    digitalWrite(FinOut, HIGH);
  }

}

void PrintInfo() {
  // Print the state of the gripper
  for (int i = 0; i < 4; i++) {
    Serial.print(currentPre[i] + atmPre);
    Serial.print(" ");
  }
  for (int i = 0; i < 4; i++) {
    if (stopFlag[i]) {
      Serial.print("T");
    } else {
      Serial.print("F");
    }
    Serial.print(" ");
  }
  for (int i = 0; i < 4; i++) {
    Serial.print(gripFlag[i]);
    Serial.print(" ");
  }
  for (int i = 0; i < 4; i++) {
      Serial.print(analogRead(BS[i]));
      Serial.print(" ");
  }
  Serial.println();

}
