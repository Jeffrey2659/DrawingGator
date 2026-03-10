#ifndef ALGO_CLASSES
#define ALGO_CLASSES

#include <Printable.h>

enum Algorithm { RAPID_LINE, SPLIT_LINE, CLW_ROTATE, CCW_ROTATE, DIRECT_MOVE };

struct Vector2d : public Printable {
  double X;
  double Y;
  Vector2d() {
    this->X = 0;
    this->Y = 0;
  }
  Vector2d(double x, double y) {
    this->X = x;
    this->Y = y;
  }
  double Magnitude() {
    return sqrt(X*X + Y*Y);
  }
  Vector2d operator+(Vector2d other) {
    return Vector2d(
      this->X + other.X,
      this->Y + other.Y
    );
  }
  Vector2d operator-(Vector2d other) {
    return Vector2d(
      this->X - other.X,
      this->Y - other.Y
    );
  }
  Vector2d operator*(double scalar) {
    return Vector2d(
      this->X * scalar,
      this->Y * scalar
    );
  }
  Vector2d operator/(double scalar) {
    return Vector2d(
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
  Vector2d start;
  Vector2d goal;
  Vector2d center;
  Algorithm algo;
  bool valid;
  unsigned int speed; // 1/4 units per minute (or per 1000 millis) (inches in our case, mm not yet configured)
  LegData() {
    start = Vector2d(0, 0);
    goal = Vector2d(0, 0);
    center = Vector2d(0, 0);
    algo = RAPID_LINE;
    valid = false;
    speed = 120; // 1/2" per second
  }
  LegData(Vector2d _start, Vector2d _goal, Algorithm alg, unsigned int move_speed) {
    start = _start;
    goal = _goal;
    center = Vector2d(0, 0);
    algo = alg;
    valid = true;
    speed = move_speed;
  }
  LegData(Vector2d _start, Vector2d _goal, Vector2d _center, Algorithm alg, unsigned int move_speed) {
    start = _start;
    goal = _goal;
    center = _center;
    algo = alg;
    valid = true;
    speed = move_speed;
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
    if (this->algo == CLW_ROTATE) {
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
