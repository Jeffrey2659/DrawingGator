#ifndef STATE_HOLDER
#define STATE_HOLDER

#include "AlgorithmClasses.h"
#include "STDClassRewrites.h"
#include <Printable.h>

struct StateHolder : public Printable {
  enum MOVE_STATE {
    STOPPED,    // Needs specific signal to idle again
    HALTED,     // Waits for user input
    IDLE,       // Can move, just not anything queued
    MOVING,     // Actively moving, can be cancelled
    RESTARTING  // Recovering from a STOPPED state
  };
  enum SERVO_STATE {
    PEN_DOWN,
    PEN_UP,
    PEN_SWAP
  };
  enum uSTEP_PREC { // microstep precision 
    uSTEP_MIN_PREC  = 0,    // No microstep, normal step
    uSTEP_LOW_PREC  = 1,    // 1/2 step microsteps
    uSTEP_MED_PREC  = 2,    // 1/4 step microsteps
    uSTEP_HIGH_PREC = 3,    // 1/8 step microsteps
    uSTEP_MAX_PREC  = 4     // 1/16 step microsteps
  };
  enum UNIT_STATE {
    ABS_INCHES = 0b00,
    ABS_MILLIS = 0b01,
    REL_INCHES = 0b10,
    REL_MILLIS = 0b11
  };
  enum UNIT_MASKS {
    ABS_REL_MASK = 0x02,
    INCH_MILLI_MASK = 0x01
  };

  bool debugMode = false;

  Vector2d curPos;
  Vector2d curOffset;
  LegData curLeg;
  LegData nextLeg;

  unsigned int curMoveSpeed = 100;
  int curPWM = 0;
  bool changedPWM = true;

  int lMove = 0;
  int rMove = 0;
  bool changedMove = false;

  bool toHalt = false;

  UNIT_STATE unitState = ABS_INCHES; 
  SERVO_STATE penState = PEN_UP;
  MOVE_STATE moveState = RESTARTING;

  StateHolder() {};

  // Unit setters (NOT YET TESTED)
  // Just did it this way cause I felt like it
  void setAbsolute() {
    unitState = unitState & (~ABS_REL_MASK); // clear bit 1
  }
  void setRelative() {
    unitState = unitState | (ABS_REL_MASK); // set bit 1+
  }
  void setInches() {
    unitState = unitState & (~INCH_MILLI_MASK); // clear bit 0
  }
  void setMillis() {
    unitState = unitState | (INCH_MILLI_MASK); // set bit 0
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

  void trySetSpeed(int new_speed) {
    if (new_speed <= 0) { return; }
    curMoveSpeed = new_speed;
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


  Vector2d toInch(Vector2d vect) {
    if (isInches()) {
      return vect; // Already in inches!
    }
    // If not inches, must be millis!
    return vect * 0.0393701; // Magic num from google, millis to inches
  }

  Vector2d toAbs(Vector2d vect) {
    if (isAbsolute()) {
      return vect; // Already absolute!
    }
    // If not absolute, must be relative
    return vect + curPos; // Make it absolute by adding to curPos
  }

  Vector2d toInchAbs(Vector2d vect) {
    vect = toInch(vect);
    vect = toAbs(vect);
    return vect;
  }


  // Debugging is god awful without this
  size_t printTo(Print& p) const {
    size_t n = 0;
    n += p.println("Printing State:");

    n += p.print("curPos: ");
    n += p.println(curPos);
    n += p.print("curOffset: ");
    n += p.println(curOffset);
    n += p.print("curCanvasPos: ");
    n += p.println(curPos - curOffset);

    n += p.print("debugMode: ");
    n += p.print(debugMode);
    n += p.print(", curPWM: ");
    n += p.print(curPWM);
    n += p.print(", changedPWM: ");
    n += p.print(changedPWM);
    n += p.print(", changedMove: ");
    n += p.print(changedMove);
    n += p.print(", toHalt: ");
    n += p.println(toHalt);

    n += p.print("(lMove,rMove): ");
    n += p.println(Vector2d(lMove, rMove));

    n += p.print("unitState: ");
    n += p.print(unitState);
    n += p.print(", penState: ");
    n += p.print(penState);
    n += p.print(", moveState: ");
    n += p.println(moveState);

    n += p.print("curLegValid: ");
    n += p.print(curLeg.valid);
    n += p.print(", nextLegValid: ");
    n += p.println(nextLeg.valid);
  
    n += p.print("curMoveSpeed: ");
    n += p.println(curMoveSpeed);

    n += p.print("End of States");
    
    return n;
  }
};


#endif // STATE_HOLDER