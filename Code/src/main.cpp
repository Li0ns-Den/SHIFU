#include "HardwareSerial.h"
#include "pins_arduino.h"
#include <Arduino.h>
#include <Adafruit_MAX31856.h>
#include <SPI.h>

const int CS_PINS[] = {2,3,4,5};
const int NUM_SENSORS = 4;

unsigned long startTime = 0;
int ptVal[8];
float tcVal[4];

Adafruit_MAX31856 maxChips[] = {
  Adafruit_MAX31856(CS_PINS[0]),
  Adafruit_MAX31856(CS_PINS[1]),
  Adafruit_MAX31856(CS_PINS[2]),
  Adafruit_MAX31856(CS_PINS[3])
};

void setup() {
  // initializing thermocouples
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (!maxChips[i].begin()) {
    Serial.println("Could not initialize thermocouple " + String(i));
    while (1) delay(10);
    }
    else {
    // Serial.println("Initialized Sensor " + String(i));
    // Set thermocouple type (e.g., K-type)
    maxChips[i].setThermocoupleType(MAX31856_TCTYPE_K);
    maxChips[i].setConversionMode(MAX31856_CONTINUOUS); 
    }
  }
  // initializing
  Serial.begin(115200);

  Serial.println("Controller initialized, press enter to continue");

  while (Serial.available() == 0) {}  // waiting

  while (Serial.available() > 0) {
    Serial.read();
  }
  startTime = millis();
  // Serial.println("STARTING");
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

  for (int i = 0; i < 4; i++) {
    tcVal[i] = maxChips[i].readThermocoupleTemperature();
    Serial.print(",");
    Serial.print(tcVal[i]);
  }

  Serial.println();
    
  delay(1);
}



