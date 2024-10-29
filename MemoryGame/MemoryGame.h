#ifndef MEMORY_GAME_H
#define MEMORY_GAME_H

#include <Adafruit_NeoPixel.h>
#include <Arduino.h>

// Pin and LED configuration
#define PIN 6
#define NUMPIXELS 7

// Button pin definitions
#define BUTTON_YELLOW 2
#define BUTTON_GREEN 3
#define BUTTON_BLUE 4

// Function prototypes
void playGame();
void gameLoop();
void handleButton(int buttonPin, int ledValue, int buttonIndex);
void showSequence();
void generateRandomSequence();
bool verifySequence();


#endif
