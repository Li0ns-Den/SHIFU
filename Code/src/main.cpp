#include "HardwareSerial.h"
#include "pins_arduino.h"
#include <Arduino.h>
// #include <SPI.h>
// #include <Adafruit_MAX31856.h>

unsigned long startTime = 0;
int ptVal[8];

void setup() {
  // initializing
  Serial.begin(115200);
  Serial.println("Initialized, press any key or enter to continue");

  while (Serial.available() == 0) {}  // waiting

  while (Serial.available() > 0) {
    Serial.read();
  }
  startTime = millis();
  Serial.println("STARTING");

}

void loop() {
  // assiging relative time to recording start
  unsigned long relTime = millis() - startTime;
  Serial.print(relTime);
  // Serial.print(",");
  // Read the analog pins
  for (int i = 0; i < 8; i++) {
    ptVal[i] = analogRead(A0 + i);
    Serial.print(",");
    Serial.print(ptVal[i]);
  }
  Serial.println();
    
  delay(30);
}



