#ifndef STATE_HOLDER
#define STATE_HOLDER

#include "AlgorithmClasses.h"
#include "CustomVector.h"

struct StateHolder {
  enum MOVE_STATE {
    STOPPED,    // Needs specific signal to idle again
    HALTED,     // Waits for user input
    IDLE,       // Can move, just not anything queued
    MOVING      // Actively moving, can be cancelled
  };
  enum SERVO_STATE {
    PEN_DOWN,
    PEN_UP,
    PEN_SWAP
  };
  enum UNIT_STATE {
    ABS_INCHES,   // 00b
    ABS_MILLIS,   // 01b
    REL_INCHES,   // 10b
    REL_MILLIS    // 11b
  };

  Point curPos;
  LegData curLeg;
  LegData nextLeg;
  double curSpeed = 1;
  int curPWM = 0;
  bool changedPWM = true;
  int lMove = 0;
  int rMove = 0;
  bool changedMove = false;
  UNIT_STATE unitState; 
  SERVO_STATE penState;
  MOVE_STATE moveState;

  StateHolder() {};

  // Unit setters (NOT YET TESTED)
  // Just did it this way cause I felt like it
  void setAbsolute() {
    unitState = unitState & 0xFD; // clear bit 1
  }
  void setRelative() {
    unitState = unitState | 0x02; // set bit 1
  }
  void setInches() {
    unitState = unitState & 0xFE; // clear bit 0
  }
  void setMillis() {
    unitState = unitState | 0x01; // set bit 0
  }

  void setPWM(int newPWM) {
    curPWM = min(max(newPWM, 70), 240); // 240 is down, 70 is up
    changedPWM = true;
  }

  void setMove(int l, int r) {
    lMove = l; 
    rMove = r;
    changedMove = true;
  }

  // Unit "getters" (NOT YET TESTED)
  // Just did it this way cause I felt like it
  bool isAbsolute() {
    return !(unitState & 0x02); // compare bit 1, true if zero
  }
  bool isRelative() {
    return !isAbsolute(); // opposites
  }
  bool isInches() {
    return !(unitState & 0x01); // compare bit 0, true if zero
  }
  bool isMillis() {
    return !isInches(); // opposites
  }

  bool hasNextLeg() {
    return nextLeg.valid; // opposites
  }


  // 
};


#endif // STATE_HOLDER