#include <Printable.h>

#ifndef ALGO_ITEMS
#define ALGO_ITEMS

enum Algorithm { OVERWRITE, GREEDY, LINE_FOLLOW, CIRCULAR };

struct Point : public Printable {
  double X;
  double Y;
  Point() {
    this->X = 0;
    this->Y = 0;
  }
  Point(double x, double y) {
    this->X = x;
    this->Y = y;
  }
  double Magnitude() {
    return sqrt(X*X + Y*Y);
  }
  Point operator+(Point other) {
    return Point(
      this->X + other.X,
      this->Y + other.Y
    );
  }
  Point operator-(Point other) {
    return Point(
      this->X - other.X,
      this->Y - other.Y
    );
  }
  Point operator*(double scalar) {
    return Point(
      this->X * scalar,
      this->Y * scalar
    );
  }
  Point operator/(double scalar) {
    return Point(
      this->X / scalar,
      this->Y / scalar
    );
  }
  size_t printTo(Print& p) const {
    size_t n = 0;
  
    n += p.print("(X=");
    n += p.print(this->X);
    n += p.print(", Y=");
    n += p.print(this->Y);
    n += p.print(")");
    return n;
  }
};

struct LegData : public Printable {
  Point start;
  Point goal;
  Point center;
  Algorithm algo;
  bool valid;
  LegData() {
    start = Point(0, 0);
    goal = Point(0, 0);
    center = Point(0, 0);
    algo = GREEDY;
    valid = false;
  }
  LegData(double sx, double sy, double gx, double gy, Algorithm alg) {
    start = Point(sx, sy);
    goal = Point(gx, gy);
    center = Point(0, 0);
    algo = alg;
    valid = true;
  }
  LegData(double sx, double sy, double gx, double gy, double cx, double cy, Algorithm alg) {
    start = Point(sx, sy);
    goal = Point(gx, gy);
    center = Point(cx, cy);
    algo = alg;
    valid = true;
  }
  size_t printTo(Print& p) const {
    size_t n = 0;

    if (!this->valid) {
      p.print("{ valid_pt=false }");
      return n;
    }

    n += p.print("{ start=");
    n += p.print(this->start);
    n += p.print(", goal=");
    n += p.print(this->goal);
    if (this->algo == CIRCULAR) {
      n += p.print(", center=");
      n += p.print(this->center);
    }
    n += p.print(", algo=");
    n += p.print(this->algo);
    n += p.print(" }");

    return n;
  }
};

double getAlgoDist(Point curLoc, LegData data) {
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

      bestDist = (1*greedWeight + 2*lineWeight) / 3;
      break;

    case CIRCULAR:
      double radius = (data.start - data.center).Magnitude();
      Point centerToPoint = (curLoc - data.center);
      Point unitCenterToPoint = centerToPoint/(centerToPoint.Magnitude());
      Point closestCircPoint = (unitCenterToPoint*radius) + data.center;
      
      greedWeight = (data.goal - curLoc).Magnitude();
      curveWeight = (closestCircPoint - curLoc).Magnitude();

      bestDist = (1*greedWeight + 2*curveWeight) / 3;
      break;

    default:
      // Shouldn't get here... uh oh.
      Serial.print("Invalid algorithm: ");
      Serial.println(data.algo);
      break;
  }
  return bestDist;
}

Point getPointFromLengths(double leftLen, double rightLen, double width) {
  double a = rightLen;
  double b = leftLen;
  double c = width;
	double toArcCos = (pow(c, 2) + pow(b, 2) - pow(a, 2)) / (2*b*c);
	double theta = acos(toArcCos); // This is angle from top bar of left rope
	double xDist = leftLen*cos(theta);
	double yDist = leftLen*sin(theta);

	return Point(xDist, yDist);
}

// X is left length, Y is right length, just using point return as packet type
Point getLengthsFromPos(Point pos, double width) {
  double leftLen = pos.Magnitude();
	double rightLen = (Point(width, 0) - pos).Magnitude();
	return Point(leftLen, rightLen);
}

#endif // ALGO_ITEMS
