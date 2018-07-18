#include <OctoWS2811.h>

// A 5 meter strip (at 60 LEDs/meter) has 300 LEDs.
// If the strip is actually RGBW, then that looks like 400 LEDs to OctoWS2811.
const int ledsPerStrip = 400;

DMAMEM int displayMemory[ledsPerStrip*6];
int drawingMemory[ledsPerStrip*6];

// Uncomment this one for typical RGB strips
//const int config = WS2811_GRB | WS2811_800kHz;

// Uncomment this one for SK2812 RGBW strips
// const int config = WS2811_RGB | WS2811_800kHz;

OctoWS2811 leds(ledsPerStrip, displayMemory, drawingMemory, config);

void setup() {
  Serial.begin(9600); // actually 12 Mbit/sec
  leds.begin();

  for (int i=0; i < leds.numPixels(); i++) {
    switch (i % 3) {
      case 0: leds.setPixel(i, 0xFF0000); break; // red
      case 1: leds.setPixel(i, 0x00FF00); break; // green
      case 2: leds.setPixel(i, 0x0000FF); break; // blue      
    }
  }
  
  leds.show();
}

// Protocol:
//
// DRAW_FRAME: 0 byte followed by ledsPerStrip*8*3 bytes
// SYNC: 255 byte - ignore all bytes until next 0 byte
//
// To sync up, write ledsPerStrip*8*3 + 1 instances of 255, followed by a 0. You
// are now at the beginning of a packet and can write DRAW_FRAME.

void loop() {
  while (! Serial.available() );
  unsigned char cmd = Serial.read();

  switch (cmd) {
    // DRAW_FRAME
    case 0: {
      for (int i=0; i < leds.numPixels(); i++) {
        uint32_t color = 0;
        for (int j = 0; j < 3; j ++) {
          while (! Serial.available() );
          color <<= 8;
          color |= (unsigned char)Serial.read();
        }
        leds.setPixel(i, color);
      }
      leds.show();
      break;
    }

    // SYNC
    case 255: {
      unsigned char ch;
      do {
        while (! Serial.available() );
        ch = Serial.read();
      } while (ch != 0);
      break;
    }

    // bad command, ignore
    default:
    break;
  }
}

