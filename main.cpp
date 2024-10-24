#include <WiFi.h>
#include <Arduino.h>

void setup() {
    pinMode(13, OUTPUT);    // LED_BUILTIN 대신 13으로 대체 가능
}

void loop() {
    digitalWrite(LED_BUILTIN, HIGH);    // LED_BUILTIN 대신 13으로 대체 가능
    delay(1000);

    digitalWrite(LED_BUILTIN, LOW);     // LED_BUILTIN 대신 13으로 대체 가능
    delay(1000);
}