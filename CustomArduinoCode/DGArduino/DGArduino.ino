#include "CustomVector.h"
#include "GCodeHandler.h"
#include "AlgorithmClasses.h"
#include "AlgorithmMethods.h"

// Output Parameters
#define SERVO_PIN 3
#define LEFT_MOTOR_DIR_PIN 6
#define LEFT_MOTOR_STEP_PIN 7
#define RIGHT_MOTOR_DIR_PIN 8
#define RIGHT_MOTOR_STEP_PIN 9

// Set mechanical parameters in AlgorithmItems.h

bool LED_on = false;
StateHolder sh;
GCodeHandler gch(sh);

void setup() {
  // Start serial communication on USB with following config:
  // Baud rate = 9600
  // 8 data bits
  // odd parity
  // 1 stop bit
  Serial.begin(9600, SERIAL_8N1);

  // Initialize internal LED (already defined)
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SERVO_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_STEP_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP_PIN, OUTPUT);
}

void loop() {
  // For now, just toggle LED when input is gotten from UART
  bool ready = gch.receiveGCode();
  bool hasCurLeg = sh.curLeg.valid;
  bool hasNextLeg = sh.nextLeg.valid;
  if (!hasCurLeg && hasNextLeg) {
    sh.curLeg = sh.nextLeg;
    sh.nextLeg = LegData();
  }
  if (sh.changedPWM) {
    sh.changedPWM = false;
    analogWrite(SERVO_PIN, sh.curPWM);
  }
  if (sh.changedMove) {
    sh.changedMove = false;
    int LDIR = (sh.lMove < 0 ? LOW : HIGH);
    int RDIR = (sh.rMove < 0 ? LOW : HIGH);
    digitalWrite(LEFT_MOTOR_DIR_PIN, LDIR);
    digitalWrite(RIGHT_MOTOR_DIR_PIN, RDIR);
    int LMOD = 100/(2*abs(sh.lMove));
    int RMOD = 100/(2*abs(sh.rMove));
    int LSTEP = LOW;
    int RSTEP = LOW;
    for (int i = 1; i < 100; i++) {
      delayMicroseconds(100);
      if (i % LMOD == 0) {
        LSTEP = (LSTEP == LOW ? HIGH : LOW);
        digitalWrite(LEFT_MOTOR_STEP_PIN, LSTEP);
      }
      if (i % RMOD == 0) {
        RSTEP = (RSTEP == LOW ? HIGH : LOW);
        digitalWrite(RIGHT_MOTOR_STEP_PIN, RSTEP);
      }
    }
    digitalWrite(LEFT_MOTOR_STEP_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_STEP_PIN, LOW);
  }
}
