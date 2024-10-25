
#include <Wire.h>
#include "Grove_LED_Matrix_Driver_HT16K33.h"
#include <Adafruit_NeoPixel.h>

#include <Servo.h>
#include <SoftwareSerial.h>
#include "WT2605C_Player.h"

#ifdef __AVR__
  #include <SoftwareSerial.h>
  SoftwareSerial SSerial(2, 3); // RX, TX
  #define COMSerial SSerial
  #define ShowSerial Serial

  WT2605C<SoftwareSerial> Mp3Player;
#endif

// Pin and LED configuration
#define LED_PIN       5
#define NUMPIXELS    37
#define MAX_FILES 4



Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN);
int LED_BRIGHTNESS = 180;  // Brightness level from 0-255 for hexagonal led

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

// Define a structure to hold audio file information
struct AudioFiles {
    const char* key;
    const char* files[MAX_FILES];
    uint8_t fileCount;
};

AudioFiles audioFiles[] = {
    {"emotion_confused", {"17"}, 1},
    {"emotion_fear", {"1"}, 1},
    {"emotion_happy", {"2"}, 1},
    {"user_understand_suggestion", {"2"}, 1},
    {"emotion_try_again", {"4"}, 1},
    {"emotion_realization", {"5"}, 1},
    {"emotion_sad", {"6"}, 1},
    {"emotion_correct", {"7"}, 1},
    {"user_dont_want_suggestion", {"8"}, 1},
    {"user_dont_want_play1", {"8"}, 1},
    {"songs", {"9"}, 1},
    {"yawns", {"10", "11"}, 2},
    {"oona", {"12", "13", "14", "15"}, 4},
    {"look", {"18"},1},
    {"your_turn", {"16"}, 1}
};

const int numAudioFiles = sizeof(audioFiles) / sizeof(AudioFiles);


int trackNumber = 0 ;// command.toInt() + (command.toInt()-1); to get the right track on the sd card SpecifyMusicPlay(trackNumber)

Matrix_8x8 matrix;

void setup() {
    ShowSerial.begin(9600);     // Start the hardware serial to communicate with PC
    COMSerial.begin(115200);    // Start software serial for MP3 module
    while (!ShowSerial);        // Wait for the serial monitor to open
    
    ShowSerial.println("Initializing MP3 Player...");
    Mp3Player.init(COMSerial);  // Initialize the MP3 player
    ShowSerial.println("MP3 Player Initialized!");
    Wire.begin();
    matrix.init();
    matrix.clear();
    matrix.setBrightness(4);
    matrix.setBlinkRate(BLINK_OFF);
    pixels.begin();
    pixels.clear();
    Serial.begin(9600);
   
    delay(100);
   
    displayStaticColor(255,20,147,150);
    
    
  
    
}

void loop() {
  
  // Check if there is any incoming data from the Serial Monitor
  if (ShowSerial.available()) {
    String input = ShowSerial.readStringUntil('\n');
    input.trim();  // Remove any whitespace

    if (input.startsWith("I - ")) {
      // Handling intent input
      String intentName = input.substring(4);  // Get the intent name after "I - "
      ShowSerial.println("Received intent: " + intentName);
      // Here, you might map intents to actions or track numbers
    }
    else if (input.startsWith("T - ")) {
      // Handling track number input
      uint32_t trackNumber = input.substring(4).toInt();  // Get the track number after "T - "
      ShowSerial.println("Playing track number: " + String(trackNumber));
      Mp3Player.playSDRootSong(trackNumber);  // Play the song by track number from the SD card
    }
  }


  //matrix.writeOnePicture(IMAGES[1]);
  //matrix.display();



}

void handleCommand(String command) {
  if (command.startsWith("T - ")) {
    int c=command.substring(4).toInt();
    trackNumber = c + (c-1); // Extract track number
    Serial.print("Playing track number: ");
    Serial.println(trackNumber);
   
  }
  if (command.startsWith("I - ")) {
    String intent = command.substring(4);
    Serial.print("Intent detected:" + intent);
  }

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



void  push_icon() { // loop of the pushing the button icon *change the condition to exit the loop
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

void countdown_matrix() { //display a 3 2 1 countodown
  matrix.clear();
  matrix.writeNumber(3,1000);
  matrix.display();

  matrix.writeNumber(2,1000);
  matrix.display();

  matrix.writeNumber(1,1000);
  matrix.display();


}

void displayStaticColor(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness) {
    for (int i = 0; i < pixels.numPixels(); i++) {
        pixels.setPixelColor(i, pixels.Color((r * brightness) / 255, (g * brightness) / 255, (b * brightness) / 255));
    }
    pixels.show(); // Update the strip to set the new colors
}

void gradientBlink(uint8_t r, uint8_t g, uint8_t b, int delayms, uint8_t brightness) {
    // Fade in
    for (int i = 0; i < 256; i++) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        pixels.show();
        delay(delayms / 512);  // Adjusted for two fades (in and out) over the same delay period
    }
    // Fade out
    for (int i = 255; i >= 0; i--) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        pixels.show();
        delay(delayms / 512);
    }
}

void setAllPixels(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness) {
    for (int i = 0; i < pixels.numPixels(); i++) {
        pixels.setPixelColor(i, pixels.Color((r * brightness) / 255, (g * brightness) / 255, (b * brightness) / 255));
    }
}

void gradientTurnOff(uint8_t r, uint8_t g, uint8_t b, int transitionTime, uint8_t brightness) {
    for (int i = 255; i >= 0; i--) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        pixels.show();
        delay(transitionTime / 256);
    }
}

void gradientTurnOn(uint8_t r, uint8_t g, uint8_t b, int transitionTime, uint8_t brightness) {
    for (int i = 0; i < 256; i++) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        pixels.show();
        delay(transitionTime / 256);
    }
}
