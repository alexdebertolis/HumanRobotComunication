#include "MemoryGame.h"

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int sequence[20]; // Increase the size to allow sequence expansion
int userSequence[20];
int previousSequence[20];
int currentStep = 0;
bool userTurn = false;
unsigned long buttonPressTime[3] = {0, 0, 0};
const unsigned long debounceDelay = 50; // Debounce time (50 ms)
const unsigned long longPressThreshold = 1000; // Maximum time allowed for button press (1000 ms)
int sequenceLength = 3; // Initial sequence length
int correctAttempts = 0; // Counter for correct attempts
int exitFlag = 0;


void playGame() {
  pixels.begin(); // Initialize the NeoPixel strip
  pixels.clear(); // Make sure all LEDs are off
  pixels.show();  // Apply the change

  // Initial sequence: turn on the strip white from left to right and then right to left
  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(150, 150, 150)); // White
    pixels.show();
    delay(200);
  }
  for (int i = NUMPIXELS - 1; i >= 0; i--) {
    pixels.setPixelColor(i, pixels.Color(150, 150, 150)); // White
    pixels.show();
    delay(200);
  }

  // Blink all LEDs twice
  for (int j = 0; j < 2; j++) {
    pixels.fill(pixels.Color(150, 150, 150)); // White
    pixels.show();
    delay(500);
    pixels.clear();
    pixels.show();
    delay(500);
  }

  delay(1000); // Wait for a second before starting the game

  // Set button pins as input
  pinMode(BUTTON_YELLOW, INPUT);
  pinMode(BUTTON_GREEN, INPUT);
  pinMode(BUTTON_BLUE, INPUT);

  randomSeed(analogRead(0)); // Initialize random number seed

  // Generate the initial random sequence
  generateRandomSequence();
  showSequence(); // Show the generated sequence

  while (exitFlag <= 5) {
    gameLoop();
  }
}

void gameLoop() {
  if (userTurn) {
    // Read buttons
    handleButton(BUTTON_YELLOW, 1, 0);
    handleButton(BUTTON_GREEN, 3, 1);
    handleButton(BUTTON_BLUE, 5, 2);

    // Check if the user has completed the sequence
    if (currentStep == sequenceLength) {
      userTurn = false;
      if (verifySequence()) {
        // If the sequence is correct
        correctAttempts++;
        exitFlag ++;
        pixels.clear();
        for (int i = 0; i < sequenceLength; i++) {
          pixels.setPixelColor(sequence[i], pixels.Color(0, 150, 0)); // Show green if correct
        }
        pixels.show();
        delay(1000);

        // Every two correct attempts, increase the sequence length
        if (correctAttempts % 2 == 0) {
          sequenceLength++;
        }
      } else {
        // If the sequence is incorrect
        correctAttempts = 0; // Reset correct attempts counter
        exitFlag ++;
        pixels.clear();
        for (int i = 0; i < NUMPIXELS; i++) {
          pixels.setPixelColor(i, pixels.Color(150, 0, 0)); // Show red if incorrect
        }
        pixels.show();
        delay(1000);
      }
      pixels.clear();
      pixels.show();
      delay(500);
      generateRandomSequence();
      delay(1000);
      showSequence();
    }
  }
}

void handleButton(int buttonPin, int ledValue, int buttonIndex) {
  int buttonState = digitalRead(buttonPin);
  unsigned long currentTime = millis();

  if (buttonState == HIGH) {
    if ((currentTime - buttonPressTime[buttonIndex]) > debounceDelay) {
      // Check if the button has not been held down for too long
      if ((currentTime - buttonPressTime[buttonIndex]) < longPressThreshold) {
        userSequence[currentStep] = ledValue;
        currentStep++;
      }
      buttonPressTime[buttonIndex] = currentTime; // Update the last press time
      delay(200); // Additional debounce to avoid multiple readings
    }
  } else {
    // Reset press time when the button is not pressed
    buttonPressTime[buttonIndex] = currentTime;
  }
}

void showSequence() {
  for (int i = 0; i < sequenceLength; i++) {
    pixels.clear();
    switch (sequence[i]) {
      case 1:
        pixels.setPixelColor(1, pixels.Color(150, 150, 0)); // Yellow
        break;
      case 3:
        pixels.setPixelColor(3, pixels.Color(0, 150, 0)); // Green
        break;
      case 5:
        pixels.setPixelColor(5, pixels.Color(0, 0, 150)); // Blue
        break;
    }
    pixels.show();
    delay(500);
    pixels.clear();
    pixels.show();
    delay(250);
  }
  userTurn = true;
  currentStep = 0;
}

void generateRandomSequence() {
  bool isSame = true;
  while (isSame) {
    for (int i = 0; i < sequenceLength; i++) {
      int ledIndex = random(0, 3);
      sequence[i] = (ledIndex == 0) ? 1 : (ledIndex == 1) ? 3 : 5; // Generate random numbers between 1, 3, and 5 (LEDs)
    }
    // Check if the new sequence is the same as the previous one
    isSame = true;
    for (int i = 0; i < sequenceLength; i++) {
      if (sequence[i] != previousSequence[i]) {
        isSame = false;
        break;
      }
    }
  }
  // Store the current sequence as the previous sequence
  for (int i = 0; i < sequenceLength; i++) {
    previousSequence[i] = sequence[i];
  }
}

bool verifySequence() {
  for (int i = 0; i < sequenceLength; i++) {
    if (userSequence[i] != sequence[i]) {
      return false;
    }
  }
  return true;
}
