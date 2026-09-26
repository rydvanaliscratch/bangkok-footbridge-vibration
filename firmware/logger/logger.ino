/*
 * Bangkok Footbridge Vibration Study - data logger
 *
 * Streams timestamped raw accelerometer samples from an MPU-6050 (GY-521)
 * over USB serial as CSV, for ambient vibration measurement of pedestrian
 * overpasses.
 *
 * Hardware: Arduino Uno R3 + GY-521. Four wires, no breadboard:
 *   VCC -> 5V      GND -> GND      SDA -> A4      SCL -> A5
 *
 * Output: one line per sample, "t_us,ax,ay,az"
 *   t_us  microseconds from micros(), rolls over every ~71 minutes
 *   ax/ay/az  signed 16-bit counts, 16384 counts per g at +/-2 g
 *
 * Design notes - the three choices that decide whether the data is usable:
 *
 *   1. DLPF is set to 21 Hz. Sampling at 200 Hz puts Nyquist at 100 Hz, so
 *      without an analogue anti-alias filter any energy above 100 Hz folds
 *      back down into the band of interest and cannot be removed afterwards.
 *      Bridge modes are below 10 Hz, so 21 Hz is generous.
 *
 *   2. The sample interval is enforced with micros(), not delay(). delay()
 *      does not account for the time the read and the print take, so the true
 *      rate drifts below the nominal one and varies with serial load.
 *
 *   3. Every sample carries its own timestamp. The analysis must use the
 *      MEASURED rate - median of diff(t_us) - never the nominal 200 Hz.
 *      Jitter smears a real spectral peak and cannot be repaired later.
 */

#include <Wire.h>

const uint8_t  MPU_ADDR      = 0x68;

const uint8_t  REG_SMPLRT_DIV   = 0x19;
const uint8_t  REG_CONFIG       = 0x1A;
const uint8_t  REG_ACCEL_CONFIG = 0x1C;
const uint8_t  REG_ACCEL_XOUT_H = 0x3B;
const uint8_t  REG_PWR_MGMT_1   = 0x6B;
const uint8_t  REG_WHO_AM_I     = 0x75;

const unsigned long SAMPLE_INTERVAL_US = 5000UL;   // 5000 us = 200 Hz

void writeReg(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU_ADDR, (uint8_t)1);
  return Wire.available() ? Wire.read() : 0xFF;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }

  Wire.begin();
  Wire.setClock(400000);          // fast-mode I2C, keeps the 6-byte read short

  delay(100);

  // Gate B1: the sensor identifies itself. 0x68 is the MPU-6050's fixed ID.
  uint8_t who = readReg(REG_WHO_AM_I);
  if (who == 0x68) {
    Serial.println("# WHO_AM_I ok (0x68)");
  } else {
    Serial.print("# WHO_AM_I FAILED, got 0x");
    Serial.println(who, HEX);
    Serial.println("# check the four solder joints and the wiring, then reset");
  }

  writeReg(REG_PWR_MGMT_1,   0x01);  // wake; clock source = gyro X (more stable than internal RC)
  delay(50);
  writeReg(REG_CONFIG,       0x04);  // DLPF_CFG = 4 -> 21 Hz accelerometer bandwidth
  writeReg(REG_ACCEL_CONFIG, 0x00);  // AFS_SEL = 0 -> +/-2 g, 16384 counts per g
  writeReg(REG_SMPLRT_DIV,   0x04);  // 1 kHz / (1 + 4) = 200 Hz internal rate
  delay(50);

  Serial.println("# MPU-6050 configured: +/-2g, DLPF 21 Hz, internal 200 Hz");
  Serial.println("# columns: t_us,ax,ay,az   counts, 16384 per g");
  Serial.println("t_us,ax,ay,az");
}

void loop() {
  static unsigned long next_us = 0;
  static bool started = false;

  if (!started) { next_us = micros(); started = true; }

  // Wait for the next slot. The signed cast makes this survive micros() rollover.
  while ((long)(micros() - next_us) < 0) { ; }
  next_us += SAMPLE_INTERVAL_US;

  unsigned long t = micros();

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(REG_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU_ADDR, (uint8_t)6);

  if (Wire.available() < 6) return;   // dropped read; the gap shows in t_us

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();

  // Raw integers, not floats: floats are slower to format and cost more bytes,
  // and the conversion to g belongs in the analysis where it is documented.
  Serial.print(t);   Serial.print(',');
  Serial.print(ax);  Serial.print(',');
  Serial.print(ay);  Serial.print(',');
  Serial.println(az);
}
