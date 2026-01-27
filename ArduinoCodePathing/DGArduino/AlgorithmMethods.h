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

#define PI 3.14159265359
const double MIN_STEP_DIST = WHEEL_RADIUS*(MIN_ROT_STEP*PI/180.0d); // inches

double getAlgoDist(Vector2d& curLoc, LegData& data) {
  double bestDist = (data.start - data.goal).Magnitude();
  double greedWeight, lineWeight, curveWeight, radius;
  Vector2d centerToPoint, unitCenterToPoint, closestCircPoint;

  switch (data.algo) {
    case RAPID_LINE:
      bestDist = (data.goal - curLoc).Magnitude();
      break;

    case SPLIT_LINE:
      double m = (data.goal.Y - data.start.Y) / (data.goal.X - data.start.X);
      double yoff = -data.start.X*m + data.start.Y;

      greedWeight = (data.goal-curLoc).Magnitude();
		  lineWeight = abs(curLoc.X*m - curLoc.Y*1 + yoff)/sqrt((m*m) + 1);

      bestDist = (1*greedWeight +  2*lineWeight) / 3;
      break;

    case CLW_ROTATE:
      radius = (data.start - data.center).Magnitude();
      centerToPoint = (curLoc - data.center);
      unitCenterToPoint = centerToPoint/(centerToPoint.Magnitude());
      closestCircPoint = (unitCenterToPoint*radius) + data.center;
      
      greedWeight = (data.goal - curLoc).Magnitude();
      curveWeight = (closestCircPoint - curLoc).Magnitude();

      bestDist = (1*greedWeight + 1*curveWeight) / 2;
      break;

    case CCW_ROTATE:
      radius = (data.start - data.center).Magnitude();
      centerToPoint = (curLoc - data.center);
      unitCenterToPoint = centerToPoint/(centerToPoint.Magnitude());
      closestCircPoint = (unitCenterToPoint*radius) + data.center;
      
      greedWeight = (data.goal - curLoc).Magnitude();
      curveWeight = (closestCircPoint - curLoc).Magnitude();

      bestDist = (1*greedWeight + 1*curveWeight) / 2;
      break;

    default:
      // Shouldn't get here... uh oh.
      Serial.print("Invalid algorithm: ");
      Serial.println(data.algo);
      break;
  }
  return bestDist;
}

Vector2d getPosFromLengths(double leftLen, double rightLen) {
  double a = rightLen;
  double b = leftLen;
  double c = CANVAS_WIDTH;
	double toArcCos = (pow(c, 2) + pow(b, 2) - pow(a, 2)) / (2*b*c);
	double theta = acos(toArcCos); // This is angle from top bar of left rope
	double xDist = leftLen*cos(theta);
	double yDist = leftLen*sin(theta);

	return Vector2d(xDist, yDist);
}


// X is left length, Y is right length, just using point return as packet type
Vector2d getLengthsFromPos(Vector2d pos) {
  double leftLen = pos.Magnitude();
	double rightLen = (Vector2d(CANVAS_WIDTH, 0) - pos).Magnitude();
	return Vector2d(leftLen, rightLen);
}

// Gets next lengths to rotate motors to
// DEPRECATED
Vector2d getBestLengthDeltas(StateHolder& stateHolder) {
  Vector2d curPos = stateHolder.getTruePos();
  Vector2d curLengths = getLengthsFromPos(curPos);
  LegData& curLegData = stateHolder.curLeg;
  Vector2d bestLengths = Vector2d(0, 0);
  double bestDist = getAlgoDist(curPos, curLegData);
  for (int i = -2; i <= 2; i++) {
    for (int j = -2; j <= 2; j++) {
      Vector2d lengths = Vector2d(i*MIN_STEP_DIST, j*MIN_STEP_DIST);
      Vector2d testPoint = getPosFromLengths(curLengths.X + lengths.X, curLengths.Y + lengths.Y);
      double curDist = getAlgoDist(testPoint, curLegData);
      if (curDist < bestDist) {
        bestDist = curDist;
        bestLengths = lengths;
      }
    }
  }
  return bestLengths; // IN INCHES
}

void movePosByLengths(Vector2d lengths, StateHolder& sh) {
  Vector2d curLens = getLengthsFromPos(sh.getTruePos());
  sh.setTruePos(getPosFromLengths(curLens.X + lengths.X, curLens.Y + lengths.Y));
}

bool isNearby(Vector2d a, Vector2d b) {
  return (a - b).Magnitude() < MIN_STEP_DIST*2;
}

void setMovesFromLeg(StateHolder& sh) {
  Vector2d curLens = getLengthsFromPos(sh.getTruePos());
  Vector2d goalLens = getLengthsFromPos(sh.curLeg.goal);
  Vector2d lengthDelta = goalLens - curLens;
  sh.lMove = round(lengthDelta.X/MIN_STEP_DIST);
  sh.rMove = round(lengthDelta.Y/MIN_STEP_DIST);
}

void checkForLegSplit(StateHolder& sh) {
  if (sh.hasNextLeg() || !sh.curLeg.valid) { return; } // Shouldn't call this function! Go!
  
  switch (sh.curLeg.algo) {
    case RAPID_LINE:
      return; // f*** it we ball, no next leg to generate from this
      break; // shouldn't get here, but just in case

    case SPLIT_LINE:
      Vector2d diff = sh.curLeg.goal - sh.curLeg.start;
      if (diff.Magnitude() < MAX_STRAIGHT_LEG_DIST) {
        return; // Good enough for gov work
      }
      // Aha! Cut the leg into its smaller right now part and the everything else part!
      Vector2d cut_diff = (diff/(diff.Magnitude()))*MAX_STRAIGHT_LEG_DIST; // unit vector * dist multiplier
      Vector2d split_point = sh.curLeg.start + diff;
      sh.nextLeg = LegData(0, 0, 0, 0, sh.curLeg.algo, sh.curLeg.speed);
      sh.nextLeg.start = split_point;
      sh.nextLeg.goal = sh.curLeg.goal;
      sh.curLeg.goal = split_point;
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
