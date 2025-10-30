char exclaim = '!';
char newline = '\n';
char carret = '\r';

enum Algorithm { GREEDY, LINE_FOLLOW, CIRCULAR };

typedef struct {
      char key;
      double value;
      bool defined;
    } KeyValueItem;

// tired of not having this. Making my own implementation
template <typename T>
class Vector {
  T* data = nullptr;
  int size = 0;
  int cap = 1;
  void growSize() {
    // should only happen when size equals capacity
    T* oldData = data;
    cap *= 2;
    data = new T[cap];
    for (int i = 0; i < size; i++) {
      data[i] = oldData[i];
    }
    delete[] oldData;
  }
  void shrinkSize() {
    // should only happen when size is less than half capacity
    T* oldData = data;
    cap /= 2; // floor divide
    data = new T[cap];
    for (int i = 0; i < size; i++) {
      data[i] = oldData[i];
    }
    delete[] oldData;
  }
public:
  Vector() {
    size = 0;
    cap = 1;
    data = new T[cap];
  }
  Vector(int capacity) {
    size = 0;
    cap = capacity;
    data = new T[cap];
  }
  Vector(const Vector& other) {
    size = other.size;
    cap = other.capacity;
    data = new T[cap];
    for (int i = 0; i < other.size; i++) {
      data[i] = other.data[i];
    }
  }
  ~Vector() {
    delete[] data;
  }

  int getSize() {
    return size;
  }
  int getCapacity() {
    return cap;
  }
  T* getData() {
    return data;
  }

  Vector& insert(T newValue, int index) {
    if (index < 0 || index > size) {
      throw("Index out of range");
    }
    if (size >= cap) {
      growSize();
    }
    data[index] = newValue;
    size++;
    return *this;
  }
  Vector& append(T newValue) {
    insert(newValue, size);
    return *this;
  }
  Vector& remove(int index) {
    if (index < 0 || index >= size) {
      throw("Index out of range");
    }
    for (int i = 0; i < size-1; i++) {
      if (i >= index) {
        data[i] = data[i+1];
      }
    }
    size--;
    if (size < cap/2) {
      shrinkSize();
    }
    return *this;
  }
  T& at(int index) {
    if (index < 0 || index >= size) {
      throw("Index out of range");
    }
    return data[index];
  }
  int find(T& value) {
    for (int i = 0; i < size-1; i++) {
      if (data[i] == value) {
        return i;
      }
    }
    return -1;
  }

  Vector& operator=(const Vector& other) {
    if (other == *this) {
      return *this;
    }
    delete[] data;
    size = other.size;
    cap = other.capacity;
    data = new T[cap];
    for (int i = 0; i < other.size; i++) {
      data[i] = other.data[i];
    }
    return *this;
  }
  bool operator==(const Vector& other) {
    if (size != other.size) {
      return false;
    }
    for (int i = 0; i < other.size; i++) {
      if (data[i] != other.data[i]) {
        return false;
      }
    }
    return true;
  }
  bool operator!=(const Vector& other) {
    return !(operator==(other));
  }
};

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
  LegData() {
    start = Point(0, 0);
    goal = Point(0, 0);
    center = Point(0, 0);
    algo = GREEDY;
  }
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
      // Shouldn't get here... uh oh.
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

bool LED_on = false;
Point curPos;
LegData curLeg;

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

// returns true if ready to read gcode line
bool gCodeRecieve() {
  if (Serial.available() > 0) {
    // Because Vector doesn't typically exist here, will be much more interesting
    char data = Serial.read();
    Serial.write(data);
    Vector<int> a;
  }
}

void loop() {
  // For now, just toggle LED when input is gotten from UART

  bool ready = gCodeRecieve();
}
