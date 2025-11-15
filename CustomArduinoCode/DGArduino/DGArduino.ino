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

int lastMoveState = -1;

void loop() {
  // ALWAYS continue receiving GCode.
  // Stopping this means cannot change state from any input
  bool ready = gch.receiveGCode();
  if (sh.moveState != lastMoveState) {
    lastMoveState = sh.moveState;
    Serial.print("Now in state ");
    Serial.println(sh.moveState, HEX);
  }
  
  if (sh.moveState == StateHolder::STOPPED || sh.moveState == StateHolder::HALTED) {
    return; // Don't do anything below
  } else if (sh.moveState == StateHolder::RESTARTING) {
    // clear out current actions
    sh.curLeg = LegData();
    sh.nextLeg = LegData();
    sh.setPWM(0); // Reset servo 

    sh.moveState = StateHolder::IDLE; // move along
    return;
  }

  if (sh.moveState == StateHolder::IDLE) {
    bool hasCurLeg = sh.curLeg.valid;
    bool hasNextLeg = sh.nextLeg.valid;
    if (!hasCurLeg && hasNextLeg) {
      sh.curLeg = sh.nextLeg;
      sh.curLeg.start = sh.getTruePos();
      sh.nextLeg = LegData();
      sh.moveState = StateHolder::MOVING; // moving stepper motors soon by leg
    } else if (sh.changedMove) {
      sh.moveState = StateHolder::MOVING; // moving stepper motors soon, but manually
    }

    if (sh.changedPWM) { // Servo should only move if not moving assembly right now
      sh.changedPWM = false;
      analogWrite(SERVO_PIN, sh.curPWM); // doesn't need to set moving, should be fast enough change
      delay(250); // give servo time to act before moving on
    }
  } // May set to move directly above
  if (sh.moveState == StateHolder::MOVING) {
    // Check if there is something to do next
    if (sh.curLeg.valid) {
      Point bestLengthDelta = getBestLengthDeltas(sh);
      movePosByLengths(bestLengthDelta, sh);
      // Check if the next point is same as current pos
      if ((bestLengthDelta/MIN_STEP_DIST).Magnitude() < MIN_STEP_DIST/2) {
        // if same as current pos, no more movements, leg is OVER!
        sh.moveState = StateHolder::IDLE;
        sh.curLeg = LegData();
      } else { // if it is different, then make the move!
        sh.lMove = round(bestLengthDelta.X/MIN_STEP_DIST);
        sh.rMove = round(bestLengthDelta.Y/MIN_STEP_DIST);
        sh.changedMove = true;
      }
    } else {
      sh.moveState == StateHolder::IDLE;
    }

    // Then, if there is, (or if a move was placed) perform the move
    if (sh.changedMove) {
      sh.changedMove = false;
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
      //delayMicroseconds(200);      
    } else { // and if no action to move, then it switches to idle
      sh.moveState = StateHolder::IDLE;
    }
  }  

}
