#include "CustomVector.h"


#ifndef GCODE_HANDLER
#define GCODE_HANDLER

enum GCommands {
  // GCOM_[COMMAND_NAME] = [gval],
  GCOM_LIN_MOVE_PEN_UP = 0,
  GCOM_LIN_MOVE_PEN_DN = 1,
  GCOM_ARC_MOVE_PEN_UP = 2,
  GCOM_ARC_MOVE_PEN_DN = 3,
  GCOM_UNITS_INCHES = 20,
  GCOM_UNITS_MILLIS = 21,
  GCOM_ABSOLUTE_POS = 90,
  GCOM_RELATIVE_POS = 91,
  GCOM_SET_CUR_POS = 92
};

enum MCommands {
  // MCOM_[COMMAND_NAME] = [mval],
  MCOM_UNCOND_HALT = 0,
  MCOM_COND_HALT = 1
};

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
      if (curChar == ' ') {
        continue; // oh no another space whatsoever will I do??? (ignore)
      }
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

  if (commandPairs.getSize() < 1) {
    Serial.println("Error: Command does not have instruction to execute");
    return false; // Uh oh!
  }
  int valAsInt = (int)(commandPairs[0].value);
  switch (commandPairs[0].key) {
    case 'G':
      switch (valAsInt) {
        case GCOM_LIN_MOVE_PEN_UP:
          Serial.println("GCOM_LIN_MOVE_PEN_UP");
          break;
        case GCOM_LIN_MOVE_PEN_DN:
          Serial.println("GCOM_LIN_MOVE_PEN_DN");
          break;
        case GCOM_ARC_MOVE_PEN_UP:
          Serial.println("GCOM_ARC_MOVE_PEN_UP");
          break;
        case GCOM_ARC_MOVE_PEN_DN:
          Serial.println("GCOM_ARC_MOVE_PEN_DN");
          break;
        case GCOM_UNITS_INCHES:
          Serial.println("GCOM_UNITS_INCHES");
          break;
        case GCOM_UNITS_MILLIS:
          Serial.println("GCOM_UNITS_MILLIS");
          break;
        case GCOM_ABSOLUTE_POS:
          Serial.println("GCOM_ABSOLUTE_POS");
          break;
        case GCOM_RELATIVE_POS:
          Serial.println("GCOM_RELATIVE_POS");
          break;
        case GCOM_SET_CUR_POS:
          Serial.println("GCOM_SET_CUR_POS");
          break;
        default:
          Serial.print("Error: G command number [");
          Serial.print(valAsInt);
          Serial.println("] does not exist.");
          return false;
          break;
      }
      break;
    case 'M':
      switch (valAsInt) {
        case GCOM_LIN_MOVE_PEN_UP:
          Serial.println("GCOM_LIN_MOVE_PEN_UP");
          break;
        default:
          Serial.print("Error: M command number [");
          Serial.print(valAsInt);
          Serial.println("] does not exist.");
          return false;
          break;
      }
      break;
    default:
      Serial.print("Error: Command letter [");
      Serial.print(commandPairs[0].key);
      Serial.println("] does not exist. Did use mean [G] or [M]?");
      return false;
      break;
  } 

  return true; // Made it this far, successfully completed!
}

// returns true if ready to read gcode line
bool receiveGCode() {
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
