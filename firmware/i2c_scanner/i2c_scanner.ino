/*
 * Gate B1 - does the sensor chip answer the Uno?
 *
 * 1. Calls every possible I2C address (1 to 126) and lists the ones that reply.
 *    Known answer: the MPU-6050 on the GY-521 replies at 0x68.
 * 2. Asks the chip at 0x68 "who are you?" (register WHO_AM_I, 0x75).
 *    Known answer: 0x68. Any other value means a different or faulty chip.
 *
 * Wiring (same as the logger): VCC->5V, GND->GND, SDA->A4, SCL->A5.
 * Serial Monitor at 115200 baud. Repeats every 5 seconds.
 */

#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) { }
  Serial.println();
  Serial.println("B1 I2C scanner");
}

void loop() {
  int found = 0;
  Serial.println("Scanning...");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();
    if (err == 0) {
      Serial.print("  Device found at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found++;
    }
  }
  Serial.print("Devices found: ");
  Serial.println(found);

  // WHO_AM_I check on the MPU-6050
  Wire.beginTransmission(0x68);
  Wire.write(0x75);
  if (Wire.endTransmission(false) == 0 && Wire.requestFrom((uint8_t)0x68, (uint8_t)1) == 1) {
    uint8_t who = Wire.read();
    Serial.print("WHO_AM_I = 0x");
    if (who < 16) Serial.print("0");
    Serial.print(who, HEX);
    Serial.println(who == 0x68 ? "  (correct: MPU-6050)" : "  (UNEXPECTED)");
  } else {
    Serial.println("WHO_AM_I: no reply from 0x68");
  }
  Serial.println("B1 RESULT: " + String((found > 0) ? "check list above" : "FAIL - nothing answered"));
  Serial.println();
  delay(5000);
}
