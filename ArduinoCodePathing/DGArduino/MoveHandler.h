#ifndef MOVE_HANDLER
#define MOVE_HANDLER

#include "StateHolder.h"

// Output Parameters
#define SERVO_PIN 3
#define LEFT_MOTOR_DIR_PIN 6
#define LEFT_MOTOR_STEP_PIN 7
#define RIGHT_MOTOR_DIR_PIN 8
#define RIGHT_MOTOR_STEP_PIN 9

void setPinModes() {
  // Initialize internal LED (already defined)
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SERVO_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_STEP_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP_PIN, OUTPUT);
}

// OLD CODE, SHOULD BE UNUSED IN FINAL
void sendMovements(StateHolder& sh) {
  int LDIR = (sh.lMove < 0 ? LOW : HIGH); // may need to reverse
  int RDIR = (sh.rMove < 0 ? LOW : HIGH); // may need to reverse
  digitalWrite(LEFT_MOTOR_DIR_PIN, LDIR);
  digitalWrite(RIGHT_MOTOR_DIR_PIN, RDIR);
  int LMOD = sh.lMove != 0 ? 5000/(2*abs(sh.lMove)) : 5000;
  int RMOD = sh.rMove != 0 ? 5000/(2*abs(sh.rMove)) : 5000;
  int LSTEP = LOW;
  int RSTEP = LOW;
  
  for (int i = 1; i < 5000; i++) {
    delayMicroseconds(20);
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


void moveToPos(StateHolder& sh) {
  int LDIR = (sh.lMove < 0 ? LOW : HIGH); // may need to reverse
  int RDIR = (sh.rMove < 0 ? LOW : HIGH); // may need to reverse
  digitalWrite(LEFT_MOTOR_DIR_PIN, LDIR);
  digitalWrite(RIGHT_MOTOR_DIR_PIN, RDIR);
  int LMOD = sh.lMove != 0 ? 5000/(2*abs(sh.lMove)) : 5000;
  int RMOD = sh.rMove != 0 ? 5000/(2*abs(sh.rMove)) : 5000;
  int LSTEP = LOW;
  int RSTEP = LOW;
  
  for (int i = 1; i < 5000; i++) {
    delayMicroseconds(20);
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


#endif // MOVE_HANDLER