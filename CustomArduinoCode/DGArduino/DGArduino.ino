#include "AlgorithmItems.h"
#include "CustomVector.h"
#include "GCodeHandler.h"

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

void loop() {
  // For now, just toggle LED when input is gotten from UART

  bool ready = receiveGCode();
}
