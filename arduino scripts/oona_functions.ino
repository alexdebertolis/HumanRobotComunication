
#include <Wire.h>
#include "Grove_LED_Matrix_Driver_HT16K33.h"
#include <Adafruit_NeoPixel.h>

// Pin and LED configuration
#define LED_PIN       4
#define NUMPIXELS    37
#define MAX_FILES 4

// Define a structure to hold audio file information

Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN);
int LED_BRIGHTNESS = 255;  // Brightness level from 0-255 for hexagonal led

byte neutral[] = { //byte structure for display_bytes function
  B1111,
  B11111,
  B111111,
  B1111111,
  B111111,
  B11111,
  B1111
};

const uint8_t IMAGES[][8] = {
{
  0b00000000,
  0b00000000,
  0b00000000,
  0b00000000,
  0b00000000,
  0b00000000,
  0b00000000,
  0b00000000
},{ // happy_face = 1
  0b00000000,
  0b00000000,
  0b01100110,
  0b01100110,
  0b00000000,
  0b10000001,
  0b01111110,
  0b00000000
},{ // question mark  =2
  0b00000000,
  0b00111100,
  0b01100110,
  0b00000110,
  0b00011100,
  0b00011000,
  0b00000000,
  0b00011000
},{
  0b00000000,
  0b00111110,
  0b01000001,
  0b01010101,
  0b01000001,
  0b01010101,
  0b01000001,
  0b00111110
},{ //state 1 push = 4
  0b00010000,
  0b00010000,
  0b01010100,
  0b00111000,
  0b00010000,
  0b00000000,
  0b01111100,
  0b01111100
},{ //state 2 push = 5
  0b00010000,
  0b00010000,
  0b00010000,
  0b01010100,
  0b00111000,
  0b00010000,
  0b01111100,
  0b01111100
},{ // x icon = 6
  0b00000000,
  0b01000010,
  0b00100100,
  0b00011000,
  0b00011000,
  0b00100100,
  0b01000010,
  0b00000000
},{ // correct = 7
  0b00000000,
  0b00000001,
  0b00000010,
  0b00000100,
  0b10001000,
  0b01010000,
  0b00100000,
  0b00000000
},{ //heart = 8
  0b00000000,
  0b00100010,
  0b01110111,
  0b01111111,
  0b01111111,
  0b00111110,
  0b00011100,
  0b00001000
}};
const int IMAGES_LEN = sizeof(IMAGES)/8;
struct AudioFiles {
    const char* key;
    const char* files[MAX_FILES];
    uint8_t fileCount;
};

AudioFiles audioFiles[] = {
    {"emotion_confused", {"001"}, 1},
    {"emotion_fear", {"002"}, 1},
    {"emotion_happy", {"003", "004"}, 2},
    {"user_understand_suggestion", {"003", "004"}, 2},
    {"emotion_try_again", {"005"}, 1},
    {"emotion_realization", {"006"}, 1},
    {"emotion_sad", {"007"}, 1},
    {"emotion_correct", {"008"}, 1},
    {"sleep_sounds", {"009"}, 1},
    {"songs", {"010"}, 1},
    {"yawns", {"011", "012"}, 2},
    {"oona", {"013", "014", "015", "016"}, 4}
};

const int numAudioFiles = sizeof(audioFiles) / sizeof(AudioFiles);


trackNumber = 0 // command.toInt() + (command.toInt()-1); to get the right track on the sd card SpecifyMusicPlay(trackNumber)

Matrix_8x8 matrix;

void setup() {
    Wire.begin();
    matrix.init();
    matrix.setBrightness(15);
    matrix.setBlinkRate(BLINK_OFF);
    pixels.begin();
    pixels.clear();
    gradientTurnOn(255,20,147,2000);
    pixels.show();
}

void loop() {

  pixels.clear();
  displayStaticColor(255,20,147)
  pixels.show();



}


// Function to get audio file numbers by key
const char** getAudioFiles(const char* key, uint8_t &count) {
    for (int i = 0; i < numAudioFiles; i++) {
        if (strcmp(audioFiles[i].key, key) == 0) {
            count = audioFiles[i].fileCount;
            return audioFiles[i].files;
        }
    }
    count = 0; // No files found
    return NULL; // Return NULL pointer if not found
}

void display_bytes(byte arr[], int hue, bool left) {
  // We will draw a circle on the display
  // It is a hexagonal matrix, which means we have to do some math to know where each pixel is on the screen

  int rows[] = {4, 5, 6, 7, 6, 5, 4};      // The matrix has 4, 5, 6, 7, 6, 5, 4 rows.
  int NUM_COLUMNS = 7;                     // There are 7 columns
  int index = (left) ? 0 : 37;             // If we draw the left eye, we have to add an offset of 37 (4+5+6+7+6=5+4)
  for (int i = 0; i < NUM_COLUMNS; i++) {
    for (int j = 0; j < rows[i]; j++) {
      int brightness = LED_BRIGHTNESS * bitRead(arr[i], (left) ? rows[i] - 1 - j : j);
      pixels.setPixelColor(index, pixels.ColorHSV((328,73,89)));
      index ++;
    }
  }
}

void displayStaticColor(uint8_t r, uint8_t g, uint8_t b) {
    for(int i = 0; i < pixels.numPixels(); i++) {
        pixels.setPixelColor(i, pixels.Color(r, g, b));
    }
    pixels.show(); // Update the strip to set the new colors
}

void  push_icon() {
  while (true) {
  matrix.clear();
  matrix.writeOnePicture(IMAGES[4]);
  matrix.display();
  delay(1000);
  matrix.writeOnePicture(IMAGES[5]);
  matrix.display();
  delay(1000);
  }
}

void countdown_matrix() {
  matrix.clear();
  matrix.writeNumber(3,1000);
  matrix.display();

  matrix.writeNumber(2,1000);
  matrix.display();

  matrix.writeNumber(1,1000);
  matrix.display();


}

void gradientBlink(uint8_t r, uint8_t g, uint8_t b, int delayms) {
  // Fade in
  for(int i = 0; i < 256; i++) {
    setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255);
    pixels.show();
    delay(delayms / 512);  // Adjusted for two fades (in and out) over the same delay period
  }
  // Fade out
  for(int i = 255; i >= 0; i--) {
    setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255);
    pixels.show();
    delay(delayms / 512);
  }
}

void setAllPixels(uint8_t r, uint8_t g, uint8_t b) {
  for(int i = 0; i < pixels.numPixels(); i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
}


void gradientTurnOff(uint8_t r, uint8_t g, uint8_t b, int transitionTime) {
  for(int i = 255; i >= 0; i--) {
    setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255);
    pixels.show();
    delay(transitionTime / 256);
  }
}

void gradientTurnOn(uint8_t r, uint8_t g, uint8_t b, int transitionTime) {
  for(int i = 0; i < 256; i++) {
    setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255);
    pixels.show();
    delay(transitionTime / 256);
  }
}
