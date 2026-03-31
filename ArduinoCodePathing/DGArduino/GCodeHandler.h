#ifndef GCODE_HANDLER
#define GCODE_HANDLER

#include "STDClassRewrites.h"
#include "AlgorithmClasses.h"
#include "AlgorithmMethods.h"
#include "StateHolder.h"
#include "ErrorResp.h"

class GCodeHandler {
public:
  enum GCommands {
    // GCOM_[COMMAND_NAME] = [gval],
    GCOM_DEBUG_MODE_T = -1,
    GCOM_GREEDY_MOVE = 0,
    GCOM_LIN_MOVE = 1,
    GCOM_ARC_MOVE_PEN_UP = 2,
    GCOM_ARC_MOVE_PEN_DN = 3,
    GCOM_DIRECT_STEPPER_MV = 6,
    GCOM_UNITS_INCHES = 20,
    GCOM_UNITS_MILLIS = 21,
    GCOM_SEND_STATE = 60,
    GCOM_ABSOLUTE_POS = 90,
    GCOM_RELATIVE_POS = 91,
    GCOM_SET_CUR_POS = 92
  };
  enum MCommands {
    // MCOM_[COMMAND_NAME] = [mval],
    MCOM_UNCOND_HALT = 0,
    MCOM_COND_HALT = 1,
    MCOM_SET_SERVO = 3,
    MCOM_CONTINUE = 108,
    MCOM_SHUTDOWN = 112,
    MCOM_RESTART = 999
  };
private:
  // Just for some test stuff
  const char exclaim = '!';
  const char new_line = '\n';
  const char car_ret = '\r';
  const char back_space = '\b';
  const char delete_key = 0x7f;
  ArrayList<char> curCommand;
  LegData storedLegData;
  StateHolder* sh;

  bool hasArg(char key, ArrayList<KeyValueItem<char, double>> commandArgs) {
    for (int i = 0; i < commandArgs.getSize(); i++) {
      if (commandArgs[i].key == key) {
        return true;
      }
    }
    if (sh->debugMode) {
      Serial.print("Missing arg: ");
      Serial.println(key);
    }
    sendErr(ERROR_ENUM::GCODE_ARG);
    return false;
  }
  double getArg(char key, ArrayList<KeyValueItem<char, double>> commandArgs) {
    for (int i = 0; i < commandArgs.getSize(); i++) {
      if (commandArgs[i].key == key) {
        return commandArgs[i].value;
      }
    }
    return 0;
  }

  bool holdData(LegData legToStore) {
    storedLegData = legToStore;
    if (!sh->nextLeg.valid) {
      sh->nextLeg = storedLegData;
      // Ok will be sent when move is done
    } else {
      sendErr(ERROR_ENUM::STATE_LEGS_FULL);
    }
  }

public:
  GCodeHandler(StateHolder& states) {
    sh = &states;
  }

  LegData getStoredLegData() {
    LegData toRet = storedLegData;
    storedLegData = LegData();
    return toRet;
  }

  ArrayList<KeyValueItem<char, double>> parseGCode(ArrayList<char> commandChars) {
    bool justSawSpace = true;
    unsigned int dataBufferIndex = 0;
    char dataBuffer[20] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    KeyValueItem<char, double> holder;
    ArrayList<KeyValueItem<char, double>> toRet;
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
  bool translateGCode(ArrayList<KeyValueItem<char, double>> commandPairs) {
    // What happens here depends on instruction and parameters
    if (commandPairs.getSize() < 1) {
      if (sh->debugMode) {
        Serial.println("Error: Command does not have instruction to execute");
      }
      // sendErr(ERROR_ENUM::GCODE_PARSE);
      return false; // Uh oh!
    }
    int valAsInt = (int)(commandPairs[0].value);
    double xoff = sh->curOffset.X;
    double yoff = sh->curOffset.Y;
    double gx, gy, cx, cy;
    int s, l, r, f;
    switch (commandPairs[0].key) {
      case 'G':
        switch (valAsInt) {
          case GCOM_DEBUG_MODE_T:
            sh->debugMode = !sh->debugMode;
            sendOk();
            break;

          case GCOM_GREEDY_MOVE:
            if (!hasArg('X', commandPairs)) { return false; }
            if (!hasArg('Y', commandPairs)) { return false; }
            gx = getArg('X', commandPairs);
            gy = getArg('Y', commandPairs);
            f = getArg('F', commandPairs);
            sh->trySetSpeed(f);
            f = sh->curMoveSpeed;
            // Idk why but this is making lines too long
            // Just changing to be SPLIT_LINE instead of RAPID_LINE as temp fix
            // Currently, G0 is alias for G1
            holdData(LegData(sh->toInchAbs(Vector2d(0.0, 0.0)), sh->toInchAbs(Vector2d(gx + xoff, gy + yoff)), RAPID_LINE, f)); // Speeeed!
            // Ok or Err sent in holdData();
            break;

          case GCOM_LIN_MOVE:
            if (!hasArg('X', commandPairs)) { return false; }
            if (!hasArg('Y', commandPairs)) { return false; }
            gx = getArg('X', commandPairs);
            gy = getArg('Y', commandPairs);
            f = getArg('F', commandPairs);
            sh->trySetSpeed(f);
            f = sh->curMoveSpeed;
            holdData(LegData(sh->toInchAbs(Vector2d(0.0, 0.0)), sh->toInchAbs(Vector2d(gx + xoff, gy + yoff)), SPLIT_LINE, f));
            // Ok or Err sent in holdData();
            break;

          case GCOM_ARC_MOVE_PEN_UP:
            if (!hasArg('X', commandPairs)) { return false; }
            if (!hasArg('Y', commandPairs)) { return false; }
            if (!hasArg('I', commandPairs)) { return false; }
            if (!hasArg('J', commandPairs)) { return false; }
            gx = getArg('X', commandPairs);
            gy = getArg('Y', commandPairs);
            cx = getArg('I', commandPairs);
            cy = getArg('J', commandPairs);
            f = getArg('F', commandPairs);
            sh->trySetSpeed(f);
            f = sh->curMoveSpeed;
            holdData(LegData(sh->toInchAbs(Vector2d(0.0, 0.0)), sh->toInchAbs(Vector2d(gx + xoff, gy + yoff)), sh->toInchAbs(Vector2d(cx + xoff, cy + yoff)), CLW_ROTATE, f));
            // Ok or Err sent in holdData();
            break;

          case GCOM_ARC_MOVE_PEN_DN:
            if (!hasArg('X', commandPairs)) { return false; }
            if (!hasArg('Y', commandPairs)) { return false; }
            if (!hasArg('I', commandPairs)) { return false; }
            if (!hasArg('J', commandPairs)) { return false; }
            gx = getArg('X', commandPairs);
            gy = getArg('Y', commandPairs);
            cx = getArg('I', commandPairs);
            cy = getArg('J', commandPairs);
            f = getArg('F', commandPairs);
            sh->trySetSpeed(f);
            f = sh->curMoveSpeed;
            holdData(LegData(sh->toInchAbs(Vector2d(0.0, 0.0)), sh->toInchAbs(Vector2d(gx + xoff, gy + yoff)), sh->toInchAbs(Vector2d(cx + xoff, cy + yoff)), CCW_ROTATE, f));
            break;

          case GCOM_DIRECT_STEPPER_MV:
            l = getArg('L', commandPairs); // No has because optional
            r = getArg('R', commandPairs); // No has because optional
            f = getArg('F', commandPairs);
            sh->trySetSpeed(f);
            f = sh->curMoveSpeed;
            // Do not convert l and r, they are step values, not absolute or rel, nor inch or milli
            holdData(LegData(sh->toInchAbs(Vector2d(0.0, 0.0)), Vector2d(l, r), DIRECT_MOVE, f));
            break;

          case GCOM_SEND_STATE:
            Serial.println(*sh);
            sendOk();
            break;

          case GCOM_UNITS_INCHES:
            sh->setInches();
            sendOk();
            break;

          case GCOM_UNITS_MILLIS:
            sh->setMillis();
            sendOk(); // NEEDS TO BE TESTED
            break;

          case GCOM_ABSOLUTE_POS:
            sh->setAbsolute();
            sendOk();
            break;

          case GCOM_RELATIVE_POS:
            sh->setRelative();
            sendOk(); // NEEDS TO BE TESTED
            break;

          case GCOM_SET_CUR_POS:
            if (!hasArg('X', commandPairs)) { return false; }
            if (!hasArg('Y', commandPairs)) { return false; }
            gx = getArg('X', commandPairs);
            gy = getArg('Y', commandPairs);
            cx = getArg('I', commandPairs);
            cy = getArg('J', commandPairs);
            // Assumed to be absolute already, never convert as rel
            sh->curPos = sh->toInch(Vector2d(cx, cy));
            sh->curOffset = sh->curPos - sh->toInch(Vector2d(gx, gy)); // Assumes offsets of 0,0 if not given
            sendOk();
            break;

          default:
            if (sh->debugMode) {
              Serial.print("Error: G command number [");
              Serial.print(valAsInt);
              Serial.println("] does not exist.");
            }
            sendErr(ERROR_ENUM::GCODE_PARSE);
            return false;
            break;
        }
        break;
      case 'M':
        switch (valAsInt) {
          case MCOM_UNCOND_HALT:
            sh->moveState = StateHolder::HALTED; // May need changin?
            sendOk();
            break;

          case MCOM_COND_HALT:
            Serial.println("MCOM_COND_HALT"); // TBD
            sendErr(ERROR_ENUM::GCODE_EXEC); // Not yet implemented
            break;

          case MCOM_SET_SERVO:
            if (!hasArg('S', commandPairs)) { return false; }
            s = getArg('S', commandPairs);

            if ((sh->penState = StateHolder::PEN_DOWN) && (s > 240)) {
              sendOk(); // If the pen is already down, just get out
              break;
            }

            sh->setPWM(s);
            if (s > 240) {                                     // May need changin?
              sh->penState = StateHolder::PEN_DOWN; 
            } else {
              sh->penState = StateHolder::PEN_UP; 
            }
            // responds OK in main code
            break;

          case MCOM_CONTINUE:
            if (!(sh->moveState == StateHolder::HALTED)) {
              sendErr(ERROR_ENUM::GCODE_EXEC);
              break;
            }
            sh->moveState = StateHolder::IDLE;
            sendOk();
            break;

          case MCOM_SHUTDOWN:
            sh->moveState = StateHolder::STOPPED;
            sendOk();
            break;

          case MCOM_RESTART:
            sh->moveState = StateHolder::RESTARTING;
            sendOk();
            break;

          default:
            if (sh->debugMode) {
              Serial.print("Error: M command number [");
              Serial.print(valAsInt);
              Serial.println("] does not exist.");
            }
            sendErr(ERROR_ENUM::GCODE_PARSE);
            return false;
            break;

        }
        break;
      default:
        if (sh->debugMode) {
          Serial.print("Error: Command letter [");
          Serial.print(commandPairs[0].key);
          Serial.println("] does not exist. Did mean to use [G] or [M]?");
        }
        sendErr(ERROR_ENUM::GCODE_PARSE);
        return false;
        break;
    } 

    return true; // Made it this far, successfully completed!
  }

  // returns true if ready to read gcode line
  bool receiveGCode() {
    while (Serial.available() > 0) {
      // Because ArrayList doesn't typically exist here, will be much more interesting
      char data = Serial.read();
      if (sh->debugMode) {
        Serial.print(data);
      }

      if (data == new_line || data == car_ret) { // Putty uses car_ret I believe, but still better to have both checked
        if (curCommand.getSize() == 0) {
          // sendErr(ERROR_ENUM::GCODE_RECEIV);
          continue; // Keep going, ignore this data
        }
        if (sh->debugMode) {
          Serial.print(">> ");
          Serial.println(curCommand.setPrintFormat(ArrayList<char>::ALPF_HORIZ_RAW));
        }
        ArrayList<KeyValueItem<char, double>> commandPairs = parseGCode(curCommand);
        bool toRet = translateGCode(commandPairs);
        curCommand.clear();
        return toRet; // parsing success
      } else if (data == back_space || data == delete_key) { // Putty can use either, mine uses delete key, better to have both I say
        curCommand.removeLast();
      } else {
        curCommand.append(data);
      }
    }
    return false;
  }
};

#endif // GCODE_HANDLER
