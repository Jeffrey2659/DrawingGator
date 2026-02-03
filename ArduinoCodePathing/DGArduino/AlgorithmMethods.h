#ifndef ALGO_METHODS
#define ALGO_METHODS

#include "AlgorithmClasses.h"
#include "StateHolder.h"

// Mechanical Parameters
#define WHEEL_RADIUS 0.5    // in inches
#define MIN_ROT_STEP 1.8    // in degrees
#define CANVAS_WIDTH 12.0   // in inches
#define MAX_STRAIGHT_LEG_DIST 0.5   // in inches
#define MAX_CURVE_LEG_DIST 0.25     // in inches

// Usefule Constants
#define PI 3.14159265359
const double MIN_STEP_DIST = WHEEL_RADIUS*(MIN_ROT_STEP*PI/180.0d); // inches


// Space Conversion
// X is left length, Y is right length for both below
Vector2d getPosFromLengths(Vector2d lengths) {
  double leftLen = lengths.X;
  double rightLen = lengths.Y;
  // refs to avoid new variable space
  double& a = rightLen;
  double& b = leftLen;
  double c = CANVAS_WIDTH;
	
  double toArcCos = (pow(c, 2) + pow(b, 2) - pow(a, 2)) / (2*b*c);
	double theta = acos(toArcCos); // This is angle from top bar of left rope
	double xDist = leftLen*cos(theta);
	double yDist = leftLen*sin(theta);

	return Vector2d(xDist, yDist);
}

Vector2d getLengthsFromPos(Vector2d pos) {
  double leftLen = pos.Magnitude();
	double rightLen = (Vector2d(CANVAS_WIDTH, 0) - pos).Magnitude();
	return Vector2d(leftLen, rightLen);
}


// Position Control
void shiftPosBySteps(StateHolder& sh, int lSteps, int rSteps) {
  Vector2d curLens = getLengthsFromPos(sh.curPos);
  curLens = curLens + Vector2d(lSteps*MIN_STEP_DIST, rSteps*MIN_STEP_DIST);
  sh.curPos = getPosFromLengths(curLens);
}

void setMovesFromLeg(StateHolder& sh) {
  Serial.println("Setting moves...");
  // INVESTIGATE TODO
  Vector2d startLens = getLengthsFromPos(sh.curLeg.start);
  Vector2d goalLens = getLengthsFromPos(sh.curLeg.goal);
  Vector2d lengthDelta = goalLens - startLens;
  sh.lMove = round(lengthDelta.X/MIN_STEP_DIST);
  sh.rMove = round(lengthDelta.Y/MIN_STEP_DIST);
  Serial.println(sh.lMove);
  Serial.println(sh.rMove);
}


// Leg Logic
void checkForLegSplit(StateHolder& sh) {
  if (sh.nextLeg.valid || !sh.curLeg.valid) { return; } // Shouldn't call this function! Go!

  sh.curLeg.start = sh.curPos; // gonna do here, since start of current leg should just be where we are
  
  switch (sh.curLeg.algo) {
    case RAPID_LINE:
      return; // f*** it we ball, no next leg to generate from this
      break; // shouldn't get here, but just in case

    case SPLIT_LINE:
      Vector2d diff = sh.curLeg.goal - sh.curLeg.start;
      if (diff.Magnitude() < MAX_STRAIGHT_LEG_DIST) {
        Serial.println("NOT LONG ENOUGH TO SPLIT");
        return; // Good enough for gov work
      }
      // Aha! Cut the leg into its smaller right now part and the everything else part!
      Vector2d cut_diff = (diff/(diff.Magnitude()))*MAX_STRAIGHT_LEG_DIST; // unit vector * dist multiplier
      Vector2d split_point = sh.curLeg.start + cut_diff;
      // if remaining dist is negligible, don't even bother making new leg
      if ((sh.curLeg.goal - split_point).Magnitude() < MIN_STEP_DIST/2) {
        sh.nextLeg = LegData(); // invalid next leg
        Serial.println("NOT ENOUGH EXTRA TO SPLIT");
        return;
      } else {
        sh.nextLeg = LegData(0, 0, 0, 0, sh.curLeg.algo, sh.curLeg.speed);
        sh.nextLeg.goal = sh.curLeg.goal;
        sh.curLeg.goal = split_point;
        Serial.println("SPLIT MADE");
      }
      break;

    case CLW_ROTATE:
      Serial.println("CW not yet implemented!");
      break;

    case CCW_ROTATE:
      Serial.println("CCW not yet implemented!");
      break;

    default:
      // Shouldn't get here... uh oh.
      Serial.print("Invalid algorithm: ");
      Serial.println(sh.curLeg.algo);
      break;
  }
}

#endif // ALGO_METHODS
