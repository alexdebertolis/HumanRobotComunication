#include "ServoMovements.h"
#include <Arduino.h>

Servo myServo1;
Servo myServo2;

void setupServos() {
  Serial.begin(9600);    
  myServo1.attach(10);   
  myServo2.attach(11);   
  myServo1.write(90);    
  myServo2.write(90);    
  delay(1000);           
}

void moveHappy() {
  for (int j = 0; j < 3; j++) {
    for (int pos = 90; pos <= 105; pos++) {
      myServo1.write(pos);
      delay(10);
    }
    for (int pos = 105; pos >= 90; pos--) {
      myServo1.write(pos);
      delay(10);
    }
    for (int pos = 90; pos >= 75; pos--) {
      myServo1.write(pos);
      delay(10);
    }
    for (int pos = 75; pos <= 90; pos++) {
      myServo1.write(pos);
      delay(10);
    }
  }
}

void moveNo() {
  for (int i = 0; i < 3; i++) {
    for (int pos = 90; pos >= 75; pos--) {
      myServo1.write(90);
      myServo2.write(pos);
      delay(10);
    }
    for (int pos = 75; pos <= 90; pos++) {
      myServo1.write(90);
      myServo2.write(pos);
      delay(10);
    }
    for (int pos = 90; pos <= 105; pos++) {
      myServo1.write(90);
      myServo2.write(pos);
      delay(10);
    }
    for (int pos = 105; pos >= 90; pos--) {
      myServo1.write(90);
      myServo2.write(pos);
      delay(10);
    }
  }
}

void moveConfused() {
  for (int pos = 90; pos >= 75; pos--) {
    myServo1.write(pos);
    delay(10);
  }
  for (int pos = 90; pos <= 115; pos++) {
    myServo2.write(pos);
    delay(10);
  }
  delay(1000);
  for (int pos = 75; pos <= 90; pos++) {
    myServo1.write(pos);
    delay(10);
  }
  for (int pos = 115; pos >= 90; pos--) {
    myServo2.write(pos);
    delay(10);
  }
}

void moveMatrix() {
  for (int pos = 90; pos >= 45; pos--) {
    myServo2.write(pos);
    delay(10);
  }
  delay(1000);
  for (int pos = 90; pos <= 105; pos++) {
    myServo1.write(pos);
    delay(10);
  }
  for (int pos = 105; pos >= 90; pos--) {
    myServo1.write(pos);
    delay(10);
  }
  for (int pos = 90; pos >= 75; pos--) {
    myServo1.write(pos);
    delay(10);
  }
  for (int pos = 75; pos <= 90; pos++) {
    myServo1.write(pos);
    delay(10);
  }
  delay(2000);
  for (int pos = 45; pos <= 90; pos++) {
    myServo2.write(pos);
    delay(10);
  }
}

void moveSleep() {
  for (int pos = 90; pos <= 105; pos++) {
    myServo1.write(pos);
    delay(10);
  }
}
