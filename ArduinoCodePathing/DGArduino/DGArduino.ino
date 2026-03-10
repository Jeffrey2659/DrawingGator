#include "STDClassRewrites.h"
#include "GCodeHandler.h"
#include "AlgorithmClasses.h"
#include "AlgorithmMethods.h"
#include "MoveHandler.h"

// Set mechanical parameters in AlgorithmItems.h

bool LED_on = false;

StateHolder sh;
MoveHandler mh;
GCodeHandler gch(sh);

void setup() {
  // Start serial communication on USB with following config:
  // Baud rate = 9600
  // 8 data bits
  // odd parity
  // 1 stop bit
  Serial.begin(9600, SERIAL_8N1);

  mh.setPinModes();
}

int lastMoveState = -1;

void loop() {
  // ALWAYS continue receiving GCode.
  // Stopping this means cannot change state from any input
  bool ready = gch.receiveGCode();

  if (sh.moveState != lastMoveState) {
    lastMoveState = sh.moveState;
    if (sh.debugMode) {
      Serial.print("Now in state ");
      Serial.println(sh.moveState, HEX);
    }
  }
  
  if (sh.moveState == StateHolder::STOPPED || sh.moveState == StateHolder::HALTED) {
    return; // Don't do anything below
  } 
  else if (sh.moveState == StateHolder::RESTARTING) {
    // clear out current actions
    sh.curLeg = LegData();
    sh.nextLeg = LegData();
    sh.setPWM(0); // Reset servo 
    sh.trySetSpeed(100); // Reset speed

    sh.moveState = StateHolder::IDLE; // move along
    return;
  } 
  else if (sh.moveState == StateHolder::IDLE) {
    bool hasCurLeg = sh.curLeg.valid;
    bool hasNextLeg = sh.nextLeg.valid;

    if (!hasCurLeg && hasNextLeg) {
      sh.curLeg = sh.nextLeg;
      sh.nextLeg = LegData();
      checkForLegSplit(sh); // split leg if needed
      setMovesFromLeg(sh); // set sh.lMove and sh.rMove
      mh.initMoves(sh); // Use sh.lMove, sh.rMove, and sh.curLeg data to init vars for moving
      sh.moveState = StateHolder::MOVING; // moving stepper motors soon by leg
    } else if (sh.changedMove) {
      sh.moveState = StateHolder::MOVING; // moving stepper motors soon, but manually
    } 

    if (sh.changedPWM) { // Servo should only move if not moving assembly right now
      sh.changedPWM = false;
      analogWrite(SERVO_PIN, sh.curPWM); // doesn't need to set moving, should be fast enough change
      delay(400); // give servo time to act before moving on
      sendOk();
    }
  } // May set to move directly above
  
  if (sh.moveState == StateHolder::MOVING) {
    // Check if there is something to do next
    if (sh.curLeg.valid) {
      mh.trySteps(sh);
    } else {
      sh.moveState == StateHolder::IDLE;
    }

    if (!sh.changedMove) {
      sh.moveState = StateHolder::IDLE;
      if (!sh.nextLeg.valid) { sendOk(); } // Only say you are done when no next leg to exec!
    }

    /* TODO: CHANGE THIS LOGIC FOR NEW ALGORITHM
    // Then, if there is, (or if a move was placed) perform the move
    if (sh.changedMove) {
      sh.changedMove = false;
      
      sendMovements(sh);
      //delayMicroseconds(200);      
    } else { // and if no action to move, then it switches to idle
      sh.moveState = StateHolder::IDLE;
      sendOk();
    }
    */
  }  

}
