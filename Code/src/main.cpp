#include "HardwareSerial.h"
#include "pins_arduino.h"
#include <Arduino.h>
#include <Adafruit_MAX31856.h>
#include <SPI.h>

const int CS_PINS[] = {2,3,4,5};
const int NUM_SENSORS = 4;

String tcTypesStr[NUM_SENSORS] = {"K", "K", "K", "T"};

unsigned long startTime = 0;
int ptVal[8];
float tcVal[4];

Adafruit_MAX31856 maxChips[] = {
  Adafruit_MAX31856(CS_PINS[0]),
  Adafruit_MAX31856(CS_PINS[1]),
  Adafruit_MAX31856(CS_PINS[2]),
  Adafruit_MAX31856(CS_PINS[3])
};

max31856_thermocoupletype_t getTypeFromString(String typeStr) {
  typeStr.toUpperCase();
  typeStr.trim();
  
  if (typeStr == "B") return MAX31856_TCTYPE_B;
  if (typeStr == "E") return MAX31856_TCTYPE_E;
  if (typeStr == "J") return MAX31856_TCTYPE_J;
  if (typeStr == "K") return MAX31856_TCTYPE_K;
  if (typeStr == "N") return MAX31856_TCTYPE_N;
  if (typeStr == "R") return MAX31856_TCTYPE_R;
  if (typeStr == "S") return MAX31856_TCTYPE_S;
  if (typeStr == "T") return MAX31856_TCTYPE_T;
  
  return MAX31856_TCTYPE_K; // Default fallback if string is invalid
}

void setup() {
  // initializing
  Serial.begin(115200);

  // initializing thermocouples
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (!maxChips[i].begin()) {
    Serial.println("Could not initialize thermocouple " + String(i));
    while (1) delay(10);
    }
    else {
    // Serial.println("Initialized Sensor " + String(i));
    // Set thermocouple type (e.g., K-type)
    max31856_thermocoupletype_t currentType = getTypeFromString(tcTypesStr[i]);
    maxChips[i].setThermocoupleType(currentType);
    maxChips[i].setConversionMode(MAX31856_CONTINUOUS); 
    }
  }
  
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



