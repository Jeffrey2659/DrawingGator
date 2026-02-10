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

struct MoveHandler {
  unsigned int leftMoves = 0;
  unsigned int rightMoves = 0;
  unsigned int lcount = 0;
  unsigned int rcount = 0;
  double LEG_EXEC_TIME = 0;
  int LSTEP = LOW;
  int RSTEP = LOW;
  int LDIR = LOW;
  int RDIR = LOW;
  unsigned long LMOD = -1;
  unsigned long RMOD = -1;

  void initMoves(StateHolder& sh) {
    leftMoves = 0;
    rightMoves = 0;
    lcount = 0;
    rcount = 0;
    LSTEP = LOW;
    RSTEP = LOW;
    LDIR = (sh.lMove < 0 ? LOW : HIGH); // may need to reverse
    RDIR = (sh.rMove < 0 ? LOW : HIGH); // may need to reverse
    digitalWrite(LEFT_MOTOR_DIR_PIN, LDIR);
    digitalWrite(RIGHT_MOTOR_DIR_PIN, RDIR);
    double quart_time = 60000.0/sh.curLeg.speed; // quarter inch time
    double leg_magnitude = (sh.curLeg.goal - sh.curLeg.start).Magnitude();
    double leg_exec_time = round(quart_time * (leg_magnitude/0.25));
    LMOD = sh.lMove != 0 ? round(leg_exec_time/(2.0*abs(sh.lMove))) : -1;
    RMOD = sh.rMove != 0 ? round(leg_exec_time/(2.0*abs(sh.rMove))) : -1;
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

  /*
  // NEED TO FIND ALTERNATIVE FOR
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
  */

  void trySteps(StateHolder& sh) {
    unsigned long millis_passed = millis();

    if ((floor(millis_passed/LMOD) > lcount) && (leftMoves < abs(sh.lMove))) {
      lcount = floor(millis_passed/LMOD); // Cannot just add, what if it skips or inits wrong?
      LSTEP = (LSTEP == LOW ? HIGH : LOW); // toggle
      digitalWrite(LEFT_MOTOR_STEP_PIN, LSTEP);
      if (LSTEP == HIGH) { 
        leftMoves++; 
        double steps_made = sh.lMove < 0 ? -1.0 : 1.0;
        shiftPosBySteps(sh, steps_made, 0.0);
      }
    }

    if ((floor(millis_passed/RMOD) > rcount) && (rightMoves < abs(sh.rMove))) {
      rcount = floor(millis_passed/RMOD); // Cannot just add, what if it skips or inits wrong?
      RSTEP = (RSTEP == LOW ? HIGH : LOW);
      digitalWrite(RIGHT_MOTOR_STEP_PIN, RSTEP);
      if (RSTEP == HIGH) { 
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
};




#endif // MOVE_HANDLER