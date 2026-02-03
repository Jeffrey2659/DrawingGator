#ifndef MOVE_HANDLER
#define MOVE_HANDLER

#include "StateHolder.h"
#include "AlgorithmClasses.h"

// Output Parameters
#define SERVO_PIN 3
#define LEFT_MOTOR_DIR_PIN 6
#define LEFT_MOTOR_STEP_PIN 7
#define RIGHT_MOTOR_DIR_PIN 8
#define RIGHT_MOTOR_STEP_PIN 9

unsigned int leftMoves = 0;
unsigned int rightMoves = 0;
int lstep = LOW;
int rstep = LOW;
int lcount = 0;
int rcount = 0;

void clearMoves() {
  leftMoves = 0;
  rightMoves = 0;
  lcount = 0;
  rcount = 0;
  lstep = LOW;
  rstep = LOW;
}

void setPinModes() {
  // Initialize internal LED (already defined)
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SERVO_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_STEP_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP_PIN, OUTPUT);
}

void moveToPos(StateHolder& sh) { // direct move
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


// NEED TO FIND ALTERNATIVE FOR
void TODO_sendMovements(StateHolder& sh) {

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

void trySteps(StateHolder& sh) {
  int LDIR = (sh.lMove < 0 ? LOW : HIGH); // may need to reverse
  int RDIR = (sh.rMove < 0 ? LOW : HIGH); // may need to reverse
  digitalWrite(LEFT_MOTOR_DIR_PIN, LDIR);
  digitalWrite(RIGHT_MOTOR_DIR_PIN, RDIR);
  double quart_time = 60000.0/sh.curLeg.speed; // quarter inch time
  double leg_magnitude = (sh.curLeg.goal - sh.curLeg.start).Magnitude();
  double leg_exec_time = round(quart_time * (leg_magnitude/0.25));
  
  int LMOD = round(sh.lMove != 0 ? leg_exec_time/(2.0*abs(sh.lMove)) : 0x0fffffff);
  int RMOD = round(sh.rMove != 0 ? leg_exec_time/(2.0*abs(sh.rMove)) : 0x0fffffff);

  unsigned long millis_passed = millis();

  if (lcount == 0) { lcount = floor(millis_passed/LMOD); }
  if (rcount == 0) { rcount = floor(millis_passed/RMOD); }

  if ((floor(millis_passed/LMOD) > lcount) && (leftMoves < abs(sh.lMove))) {
    lcount++;
    lstep = (lstep == LOW ? HIGH : LOW); // toggle
    digitalWrite(LEFT_MOTOR_STEP_PIN, lstep);
    if (lstep == HIGH) { 
      leftMoves++; 
      double steps_made = sh.lMove < 0 ? -1.0 : 1.0;
      shiftPosBySteps(sh, steps_made, 0.0);
    }
  }

  if ((floor(millis_passed/RMOD) > rcount) && (rightMoves < abs(sh.rMove))) {
    rcount++;
    rstep = (rstep == LOW ? HIGH : LOW);
    digitalWrite(RIGHT_MOTOR_STEP_PIN, rstep);
    if (rstep == HIGH) { 
      rightMoves++; 
      double steps_made = sh.rMove < 0 ? -1.0 : 1.0;
      shiftPosBySteps(sh, 0.0, steps_made);
    }
  }

  if ((rightMoves >= abs(sh.rMove)) && (leftMoves >= abs(sh.lMove))) {
    sh.curLeg = LegData(); // invalid leg
    sh.changedMove = false;
  } else {
    sh.changedMove = true;
  }

}


#endif // MOVE_HANDLER