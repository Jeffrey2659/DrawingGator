

char exclaim = '!';
char newline = '\n';
char carret = '\r';

bool LED_on = false;

enum Algorithm { GREEDY, LINE_FOLLOW, CIRCULAR };

struct Point {
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
};

struct LegData {
  Point start;
  Point goal;
  Point center;
  Algorithm algo;
  LegData(double sx, double sy, double gx, double gy, Algorithm alg) {
    start = Point(sx, sy);
    goal = Point(gx, gy);
    center = Point(0, 0);
    algo = alg;
  }
  LegData(double sx, double sy, double gx, double gy, double cx, double cy, Algorithm alg) {
    start = Point(sx, sy);
    goal = Point(gx, gy);
    center = Point(cx, cy);
    algo = alg;
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
      // Shouldn't get here... uh oh
      break;
  }

  return bestDist;
}


void setup() {
  // Start serial communication on USB with following config:
  // Baud rate = 9600
  // 8 data bits
  // No parity
  // 1 stop bit
  Serial.begin(9600, SERIAL_8N1);

  // Initialize internal LED (already defined)
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // For now, just toggle LED when input is gotten from UART
  if (Serial.available() > 0) {
    // Echo it back, and echo an exclamation point
    char data = Serial.read();
    Serial.write(data);
    Serial.write(exclaim);
    if (data == 'T') {
      Serial.write(exclaim);
      digitalWrite(LED_BUILTIN, LED_on ? LOW : HIGH);
      LED_on = !LED_on;
    }
    Serial.write(newline);
    Serial.write(carret);
  }
}
