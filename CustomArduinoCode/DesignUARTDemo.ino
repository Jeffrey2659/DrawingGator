char exclaim = '!';
char newline = '\n';
char carret = '\r';

bool LED_on = false;

int 

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
