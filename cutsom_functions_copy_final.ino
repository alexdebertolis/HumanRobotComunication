#include <Wire.h>
#include "HUSKYLENS.h"
#include "Grove_LED_Matrix_Driver_HT16K33.h"
#include <Adafruit_NeoPixel.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include "ServoMovements.h"
#include <MemoryGame.h>
// to call the game -> playGame(exitFlag);

// Pin and LED configuration
#define LED_PIN   5
#define NUMPIXELS 37
#define MAX_FILES 4

///////////////////////////////////////////////
//husky lens variable
HUSKYLENS huskylens;
bool faceRecognized = false; // Bandera que indica si se detectó una cara
////
Adafruit_NeoPixel neopixelStrip(NUMPIXELS, LED_PIN);
int LED_BRIGHTNESS = 180;  // Brightness level from 0-255 for hexagonal led
/// bottons for the game
const int boton2Pin = 2;  // Pin al que está conectado el botón 1
const int boton3Pin = 3;  // Pin al que está conectado el botón 2
const int boton4Pin = 4;  // Pin al que está conectado el botón 3


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
},{// dice 3
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
},{ //heart = 6
  0b00000000,
  0b00100010,
  0b01110111,
  0b01111111,
  0b01111111,
  0b00111110,
  0b00011100,
  0b00001000
},{ //play = 7
  0b00100000,
  0b00110000,
  0b00111000,
  0b00111100,
  0b00111000,
  0b00110000,
  0b00100000,
  0b00000000
}};
const int IMAGES_LEN = sizeof(IMAGES)/8;
Matrix_8x8 matrix;

void setup() {
  // buttons 
    pinMode(boton2Pin, INPUT);
    pinMode(boton3Pin, INPUT);
    pinMode(boton4Pin, INPUT);
  //star serial communication
  // config red matriz
    Wire.begin();
    matrix.init();
    matrix.clear();
    matrix.setBrightness(4);
    matrix.setBlinkRate(BLINK_OFF);
    matrix.writeOnePicture(IMAGES[0]);
    matrix.display();
  //config rgb matriz
    neopixelStrip.begin();
    neopixelStrip.clear();
  // config for the servos
    setupServos();
  // config for the huskylens 
  //serial 
    Serial.begin(9600);
  // delay to set all the configs
    delay(100);
  //color for the rgb matriz
    displayStaticColor(255,20,147,150);  
  // config huskylens
    if (!huskylens.begin(Wire)) {
      while (1);
    }
    // Pon el modo de detección de rostro
    huskylens.writeAlgorithm(ALGORITHM_FACE_RECOGNITION);
}



void loop() {
  // Llama a la función para detectar caras antes de detectar datos del Serial
  faceRecognized = faceDetected();
  delay(10);
  if (faceRecognized == true){
      // Si se detecta una cara
      ///
      delay (1);
      matrix.writeOnePicture(IMAGES[6]);
      matrix.display();
      moveHappy();
      delay(500);
      
      //
  }
  // Lógica de manejo del Serial solo si se reconoce una cara
  while (faceRecognized == true) {
    if (Serial.available() > 0) {  // Asegurarse de que hay datos disponibles para leer
      String input = Serial.readStringUntil('\n');
      input.trim();  // Remove any whitespace
      //// 
        delay(100);// Play the song by track number from the SD card
        ////
      
      if (input.length() > 0 && input.startsWith("I")) {  // Verificar que se hayan recibido caracteres
        // Handling intent input
        String intentName = input.substring(1);  // Get the intent name after "I - "
        //
        if (intentName == "1") {
            emotionHappy();
        }

        if (intentName == "2"){
          emotionConfused();
        }

        if (intentName == "3"){
          
          game();
          delay(1000);
           matrix.writeOnePicture(IMAGES[6]);
           matrix.display();
           delay(10);
           moveHappy();
           delay(2000);
           emotionHappy();
           
        }
        if (intentName == "0") {
          delay(1000);
          neopixelStrip.clear();
          neopixelStrip.show();
          matrix.clear();
          matrix.display();
          // servo movements
          moveSleep();


        }
        if (intentName == "9") {
          moveHappy();
          delay(500);
          moveHappy();
          delay(500);
          moveHappy();
          delay(500);
          moveHappy();
          delay(500);
        }
      }
    }
  }
}

void emotionHappy(){
  matrix.writeOnePicture(IMAGES[1]);
  matrix.display();
  delay(10);
  moveHappy();
  delay(2000);
  matrix.writeOnePicture(IMAGES[7]);
  matrix.display();
  delay(100);
  moveMatrix();
  delay(10);
  moveMatrix();
  delay(10);
}

void emotionConfused (){
  matrix.writeOnePicture(IMAGES[2]);
  matrix.display();
  delay(10);
  moveConfused();
  delay(2000);
  matrix.writeOnePicture(IMAGES[7]);
  matrix.display();
  delay(100);
  moveMatrix();
  delay(10);
  moveMatrix();
  delay(10);
}

void game (){
  push_icon();
  delay(2000);
  


  // Ejecutar `playGame()` una vez que se haya presionado cualquiera de los botones
  playGame();
  

}
// detect the face 
bool faceDetected() {
  if (huskylens.request()) {
    if (huskylens.isLearned() && huskylens.available()) {
      return true;
    } else {
      //for not entering the loop og getting the string for the serial port
      return false;
    }
  }
  return false; // Devuelve false si no se pudo hacer la solicitud
}

void push_icon() { 
    matrix.clear();
    matrix.writeOnePicture(IMAGES[4]);
    matrix.display();
    delay(500);
    matrix.writeOnePicture(IMAGES[5]);
    matrix.display();
    delay(500);
    matrix.clear();
    matrix.writeOnePicture(IMAGES[4]);
    matrix.display();
    delay(500);
    matrix.writeOnePicture(IMAGES[5]);
    matrix.display();
    delay(500);
    matrix.clear();
    matrix.writeOnePicture(IMAGES[4]);
    matrix.display();
    delay(500);
    matrix.writeOnePicture(IMAGES[5]);
    matrix.display();
    delay(500);
    matrix.clear();
    matrix.writeOnePicture(IMAGES[4]);
    matrix.display();
    delay(500);
    matrix.writeOnePicture(IMAGES[5]);
    matrix.display();
    delay(500);
}


void displayStaticColor(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness) {
    for (int i = 0; i < neopixelStrip.numPixels(); i++) {
        neopixelStrip.setPixelColor(i, neopixelStrip.Color((r * brightness) / 255, (g * brightness) / 255, (b * brightness) / 255));
    }
    neopixelStrip.show(); // Update the strip to set the new colors
}

void gradientBlink(uint8_t r, uint8_t g, uint8_t b, int delayms, uint8_t brightness) {
    // Fade in
    for (int i = 0; i < 256; i++) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        neopixelStrip.show();
        delay(delayms / 512);  // Adjusted for two fades (in and out) over the same delay period
    }
    // Fade out
    for (int i = 255; i >= 0; i--) {
        setAllPixels((r * i) / 255, (g * i) / 255, (b * i) / 255, brightness);
        neopixelStrip.show();
        delay(delayms / 512);
    }
}

void setAllPixels(uint8_t r, uint8_t g, uint8_t b, uint8_t brightness) {
    for (int i = 0; i < neopixelStrip.numPixels(); i++) {
        neopixelStrip.setPixelColor(i, neopixelStrip.Color((r * brightness) / 255, (g * brightness) / 255, (b * brightness) / 255));
    }
}

