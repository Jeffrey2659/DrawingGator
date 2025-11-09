#include <Printable.h>


#ifndef CUSTOM_VECT
#define CUSTOM_VECT

// tired of not having this. Making my own implementation

// To use vector as a psuedo map, if desired
template <typename TK, typename TV>
struct KeyValueItem: public Printable {
  TK key;
  TV value;
  size_t printTo(Print& p) const {
    size_t n = 0;
    n += p.print("( ");
    n += p.print(key);
    n += p.print(": ");
    n += p.print(value);
    n += p.print(" )");
    return n;
  }
};

template <typename T>
class Vector : public Printable {
public:
  enum VecPrintFormat { VPF_HORIZ_FANCY, VPF_HORIZ_RAW, VPF_VERT_FANCY, VPF_VERT_RAW };
private:
  T* data = nullptr;
  int size = 0;
  int cap = 1;
  VecPrintFormat printFormat = VPF_HORIZ_FANCY;
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
    cap = other.cap;
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
  VecPrintFormat getPrintFormat() {
    return printFormat;
  }
  Vector& setPrintFormat(VecPrintFormat newFormat) {
    printFormat = newFormat;
    return *this;
  }

  Vector& clear() {
    size = 0;
    cap = 1;
    delete[] data;
    data = new T[cap];
  }
  Vector& insert(T newValue, int index) {
    if (index < 0 || index > size) {
      Serial.print("insert() Err: Index out of range: ");
      Serial.println(index);
      return *this;
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
  Vector& appendRef(T& newValue) {
    insert(newValue, size);
    return *this;
  }
  Vector& remove(int index) {
    if (index < 0 || index >= size) {
      Serial.print("remove() Err: Index out of range: ");
      Serial.println(index);
      return *this;
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
  Vector& removeLast() {
    return remove(size-1);
  }
  T& at(unsigned int index) {
    if (index < 0 || index >= size) {
      Serial.print("at() Err: Index out of range: ");
      Serial.println(index);
      Serial.println("at() Warn: returning data[0]: ");
      return data[0];
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
  T& operator[](unsigned int index) {
    return at(index);
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

  size_t printTo(Print& p) const {
    size_t n = 0;
    // empty case
    if (size == 0) {
      n += p.println("[]");
      return n;
    }

    switch (printFormat) {
      case VPF_HORIZ_FANCY:
        n += p.print("[ ");
        n += p.print(data[0]);
        for (int i = 1; i < size; i++) {
          n += p.print(", ");
          n += p.print(data[i]);
        }
        n += p.print(" ]");
        break;
        
      case VPF_HORIZ_RAW:
        for (int i = 0; i < size; i++) {
          n += p.print(data[i]);
        }
        break;

      case VPF_VERT_FANCY:
        n += p.println("[... ");
        n += p.print(data[0]);
        for (int i = 1; i < size; i++) {
          n += p.println(", ");
          n += p.print(data[i]);
        }
        n += p.println();
        n += p.print("...]");
        break;

      case VPF_VERT_RAW:
        for (int i = 0; i < size-1; i++) {
          n += p.println(data[i]);
        }
        n += p.print(data[size-1]);
        break;

      default:
        n += p.print("Invalid VectorPrintFormat: ");
        n += p.print(printFormat);
        break;
    }

    return n;
  }

  void printraw() {
    for (int i = 1; i < size; i++) {
      Serial.print(data[i]);
    }
  }
};

#endif // CUSTOM_VECT
