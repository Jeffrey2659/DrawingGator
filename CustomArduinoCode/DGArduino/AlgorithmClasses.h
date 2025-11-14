#ifndef ALGO_CLASSES
#define ALGO_CLASSES

#include <Printable.h>

enum Algorithm { GREEDY, LINE_FOLLOW, CIRCULAR };

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
      p.print("{ valid_leg=false }");
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

#endif // ALGO_CLASSES
