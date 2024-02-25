#include <FastLED.h>

#define NUM_LEDS 60
#define DATA_PIN 3
#define BRIGHTNESS 100
#define interval 50;

CRGB leds[NUM_LEDS];

unsigned long prevTime = 0;
int num;
bool blink = true;

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  Serial.begin(9600);
  delay(1000);
}

void loop() {
  FastLED.setBrightness(BRIGHTNESS);
  if (Serial.available()) {
      String a = Serial.readStringUntil('\n');
      num = a.toInt();
    if (num <= NUM_LEDS) {
      FastLED.clear();
      fill_solid(leds, num, CRGB::Red);
    }
  }
  if (num+5 > NUM_LEDS) {
    long diff = millis() - prevTime;
    if (diff > 50) {
      FastLED.setBrightness(0);
      if (diff > 100)
        prevTime = millis();
    }
    
  }
  FastLED.show();
}