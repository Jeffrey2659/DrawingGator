#include "CustomVector.h"


#ifndef GCODE_HANDLER
#define GCODE_HANDLER

// Just for some test stuff
char exclaim = '!';
char new_line = '\n';
char car_ret = '\r';
char back_space = '\b';
char delete_key = 0x7f;

Vector<char> curCommand;

Vector<KeyValueItem<char, double>> parseGCode(Vector<char> commandChars) {
  bool justSawSpace = true;
  unsigned int dataBufferIndex = 0;
  char dataBuffer[20] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  KeyValueItem<char, double> holder;
  Vector<KeyValueItem<char, double>> toRet;
  for (int i = 0; i < commandChars.getSize(); i++) {
    char curChar = commandChars[i];

    // Command letter or parameter label
    if (justSawSpace) {
      holder.key = curChar;
      justSawSpace = false;
      continue;
    }

    // Package chunk of data and store, then restart for next chunk
    if (curChar == ' ') {
      dataBuffer[dataBufferIndex++] = '\0';
      holder.value = String(dataBuffer).toDouble();
      dataBufferIndex = 0;
      justSawSpace = true;
      toRet.append(holder);
      continue;
    }

    dataBuffer[dataBufferIndex++] = curChar;
  }

  dataBuffer[dataBufferIndex++] = '\0';
  holder.value = String(dataBuffer).toDouble();
  toRet.append(holder);
  return toRet;
}

// Handles parsing and performing the g-code 
bool executeGCode(Vector<KeyValueItem<char, double>> commandPairs) {
  commandPairs.setPrintFormat(VPF_VERT_FANCY); // Just stylistic choice
  Serial.println(commandPairs);

  Serial.println("Placeholder Print for Executing GCode");
  // What happens here depends on instruction and parameters
}

// returns true if ready to read gcode line
bool gCodeReceive() {
  if (Serial.available() > 0) {
    // Because Vector doesn't typically exist here, will be much more interesting
    char data = Serial.read();
    Serial.print(data);

    if (data == new_line || data == car_ret) { // Putty uses car_ret I believe, but still better to have both checked
      Serial.print(">> ");
      Serial.println(curCommand.setPrintFormat(VPF_HORIZ_RAW));
      Vector<KeyValueItem<char, double>> commandPairs = parseGCode(curCommand);
      executeGCode(commandPairs);
      curCommand.clear();
    } else if (data == back_space || data == delete_key) { // Putty can use either, mine uses delete key, better to have both I say
      curCommand.removeLast();
    } else {
      curCommand.append(data);
    }
  }
}

#endif // GCODE_HANDLER
