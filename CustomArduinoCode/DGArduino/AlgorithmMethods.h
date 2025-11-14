#ifndef ALGO_METHODS
#define ALGO_METHODS

#include "AlgorithmClasses.h"
#include "StateHolder.h"

// Mechanical Parameters
#define WHEEL_RADIUS 0.5    // in inches
#define MIN_ROT_STEP 1.8    // in degrees
#define CANVAS_WIDTH 10.0   // in inches
#define MOUNT_V_OFFSET 3.5  // in inches
#define MOUNT_H_OFFSET 2.125 // in inches
#define HLDR_WIRE_HDIST 1.0 // in inches
#define HLDR_PEN_VDIST 0.5  // in inches

#define PI 3.14159265359
const double MIN_STEP_DIST = WHEEL_RADIUS*(MIN_ROT_STEP*PI/180.0d); // inches


double getAlgoDist(Point curLo  c, LegData data) {
  double bestDist = (data.start - data.goal).Magnitude();
  double greedWeight, lineWeight, curveWeight;

  switch (data.algo) {
    case GREEDY:
      bestDist = (data.goal - curLoc).Magnitude();
      break;

    case LINE_FOLLOW:
      double m = (data.goal.Y - data.start.Y) / (data.goal.X - data.start.X);
      double yoff = -data.start.X*m + data.start.Y;

      greedWeight = (data.goal-curLoc).Magnitude();
		  lineWeight = abs(curLoc.X*m - curLoc.Y*1 + yoff)/sqrt((m*m) + 1);

      bestDist = (1*greedWeight +  2*lineWeight) / 3;
      break;

    case CIRCULAR:
      double radius = (data.start - data.center).Magnitude();
      Point centerToPoint = (curLoc - data.center);
      Point unitCenterToPoint = centerToPoint/(centerToPoint.Magnitude());
      Point closestCircPoint = (unitCenterToPoint*radius) + data.center;
      
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

Point getPointFromLengths(double leftLen, double rightLen) {
  double a = rightLen;
  double b = leftLen;
  double c = CANVAS_WIDTH;
	double toArcCos = (pow(c, 2) + pow(b, 2) - pow(a, 2)) / (2*b*c);
	double theta = acos(toArcCos); // This is angle from top bar of left rope
	double xDist = leftLen*cos(theta);
	double yDist = leftLen*sin(theta);

	return Point(xDist, yDist);
}

// X is left length, Y is right length, just using point return as packet type
Point getLengthsFromPos(Point pos) {
  double leftLen = pos.Magnitude();
	double rightLen = (Point(CANVAS_WIDTH, 0) - pos).Magnitude();
	return Point(leftLen, rightLen);
}

// Gets next lengths to rotate motors to
Point getBestLengthDeltas(StateHolder& stateHolder) {
  Point& curPos = stateHolder.curPos;
  Point curLengths = getLengthsFromPos(curPos);
  LegData& curLegData = stateHolder.curLeg;
  Point bestLengths = Point(0, 0);
  double bestDist = getAlgoDist(curPos, curLegData);
  for (int i = -2; i <= 2; i++) {
    for (int j = -2; j <= 2; j++) {
      Point lengths = Point(i*MIN_STEP_DIST, j*MIN_STEP_DIST);
      Point testPoint = getPointFromLengths(curLengths.X + lengths.X, curLengths.Y + lengths.Y);
      double curDist = getAlgoDist(testPoint, curLegData);
      if (curDist < bestDist) {
        bestDist = curDist;
        bestLengths = lengths;
      }
    }
  }
  return bestLengths; // IN INCHES
}

void movePosByLengths(Point lengths, StateHolder& sh) {
  Point curLens = getLengthsFromPos(sh.curPos);
  sh.curPos = getPointFromLengths(curLens.X + lengths.X, curLens.Y + lengths.Y);
}

#endif // ALGO_METHODS
