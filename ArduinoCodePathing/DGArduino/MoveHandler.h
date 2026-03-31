#ifndef MOVE_HANDLER
#define MOVE_HANDLER

#include "StateHolder.h"
#include "AlgorithmClasses.h"
#include "AlgorithmMethods.h"

// Output Parameters
#define SERVO_PIN 3
#define LEFT_MOTOR_DIR_PIN 6
#define LEFT_MOTOR_STEP_PIN 7
#define RIGHT_MOTOR_DIR_PIN 8
#define RIGHT_MOTOR_STEP_PIN 9
#define MICRO_STEP_CTRL_0 10
#define MICRO_STEP_CTRL_1 11
#define MICRO_STEP_CTRL_2 12


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

  void setuStepMode(StateHolder& sh, StateHolder::uSTEP_PREC newPrec) {
    switch(newPrec) {
      case StateHolder::uSTEP_MIN_PREC:
        digitalWrite(MICRO_STEP_CTRL_0, LOW);
        digitalWrite(MICRO_STEP_CTRL_1, LOW);
        digitalWrite(MICRO_STEP_CTRL_2, LOW);
        break;
      case StateHolder::uSTEP_LOW_PREC: 
        digitalWrite(MICRO_STEP_CTRL_0, HIGH);
        digitalWrite(MICRO_STEP_CTRL_1, LOW);
        digitalWrite(MICRO_STEP_CTRL_2, LOW);
        break;
      case StateHolder::uSTEP_MED_PREC:
        digitalWrite(MICRO_STEP_CTRL_0, LOW);
        digitalWrite(MICRO_STEP_CTRL_1, HIGH);
        digitalWrite(MICRO_STEP_CTRL_2, LOW);
        break;
      case StateHolder::uSTEP_HIGH_PREC:
        digitalWrite(MICRO_STEP_CTRL_0, HIGH);
        digitalWrite(MICRO_STEP_CTRL_1, HIGH);
        digitalWrite(MICRO_STEP_CTRL_2, LOW);
        break;
      case StateHolder::uSTEP_MAX_PREC:
        digitalWrite(MICRO_STEP_CTRL_0, HIGH);
        digitalWrite(MICRO_STEP_CTRL_1, HIGH);
        digitalWrite(MICRO_STEP_CTRL_2, HIGH);
        break;
      default:
        return; // not real state, do not set value
    }
    sh.ustepState = newPrec;
  }

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
    double leg_magnitude = sh.curLeg.algo == DIRECT_MOVE ? 
          (sh.curLeg.goal * MIN_STEP_DIST_NO_uSTEPS).Magnitude() : 
          (sh.curLeg.goal - sh.curLeg.start).Magnitude(); // Bad Magnitude for direct move! How to fix...
    double leg_exec_time = round(quart_time * (leg_magnitude/0.25));
    LMOD = sh.lMove != 0 ? round(leg_exec_time/(2.0*abs(sh.lMove))) : -1;
    RMOD = sh.rMove != 0 ? round(leg_exec_time/(2.0*abs(sh.rMove))) : -1;
    digitalWrite(LEFT_MOTOR_STEP_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_STEP_PIN, LOW);
  }

  void setPinModes() {
    // Initialize internal LED (already defined)
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(SERVO_PIN, OUTPUT);
    pinMode(LEFT_MOTOR_DIR_PIN, OUTPUT);
    pinMode(LEFT_MOTOR_STEP_PIN, OUTPUT);
    pinMode(RIGHT_MOTOR_DIR_PIN, OUTPUT);
    pinMode(RIGHT_MOTOR_STEP_PIN, OUTPUT);
    pinMode(MICRO_STEP_CTRL_0, OUTPUT);
    pinMode(MICRO_STEP_CTRL_1, OUTPUT);
    pinMode(MICRO_STEP_CTRL_2, OUTPUT);
  }

  void trySteps(StateHolder& sh) {
    unsigned long millis_passed = millis();

    if ((floor(millis_passed/LMOD) > lcount) && (leftMoves < abs(sh.lMove))) {
      lcount = floor(millis_passed/LMOD); // Cannot just add, what if it skips or inits wrong?
      LSTEP = (LSTEP == LOW ? HIGH : LOW); // toggle
      digitalWrite(LEFT_MOTOR_STEP_PIN, LSTEP);
      if (LSTEP == HIGH) { 
        leftMoves++; 
        int steps_made = sh.lMove < 0 ? -1 : 1;
        shiftPosBySteps(sh, steps_made, 0);
      }
    }

    if ((floor(millis_passed/RMOD) > rcount) && (rightMoves < abs(sh.rMove))) {
      rcount = floor(millis_passed/RMOD); // Cannot just add, what if it skips or inits wrong?
      RSTEP = (RSTEP == LOW ? HIGH : LOW);
      digitalWrite(RIGHT_MOTOR_STEP_PIN, RSTEP);
      if (RSTEP == HIGH) { 
        rightMoves++; 
        int steps_made = sh.rMove < 0 ? -1 : 1;
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