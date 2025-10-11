#include <Arduino.h>

const int stepPin = 3;
const int dirPin = 2;
// put function declarations here:

const int enPin = 7;



void setup() {
  // put your setup code here, to run once:
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  delay(2000);
  digitalWrite(dirPin, HIGH); // Set direction to clockwise
  pinMode(enPin, OUTPUT);
  digitalWrite(enPin, LOW); // Enable driver


}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(stepPin, HIGH);
  delay(250);
  digitalWrite(stepPin, LOW);
  delay(250);
}

