#ifndef SERVOMOVEMENTS_H
#define SERVOMOVEMENTS_H

#include <Servo.h>


extern Servo myServo1;
extern Servo myServo2;


void setupServos();  
void moveHappy();
void moveNo();
void moveConfused();
void moveMatrix();
void moveSleep();

#endif
