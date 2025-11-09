// TBD, may use to return error messages;


#ifndef ERR_RESPONSE
#define ERR_RESPONSE
struct ERROR_ENUM {
  enum Error {
    GENERIC,
    GCODE_RECEIV,
    GCODE_PARSE,
    GCODE_EXEC,
    GCODE_ARG,
    STATE_LEGS_FULL
  };
};


void sendErr(ERROR_ENUM::Error errCode) {
  Serial.print("ERR: [0x");
  Serial.print(errCode, HEX);
  Serial.print("]");
  switch(errCode) {
    case ERROR_ENUM::GCODE_RECEIV:
      Serial.println("GCODE_RECEIV");
      break;
    case ERROR_ENUM::GCODE_PARSE:
      Serial.println("GCODE_PARSE");
      break;
    case ERROR_ENUM::GCODE_EXEC:
      Serial.println("GCODE_EXEC");
      break;
    case ERROR_ENUM::GCODE_ARG:
      Serial.println("GCODE_ARG");
      break;
    case ERROR_ENUM::STATE_LEGS_FULL:
      Serial.println("STATE_LEGS_FULL");
      break;
    case ERROR_ENUM::GENERIC:
      Serial.println("GENERIC");
      break;
    default:
      Serial.println("UNKNOWN");
      break;
  }
}

#endif // ERR_RESPONSE
