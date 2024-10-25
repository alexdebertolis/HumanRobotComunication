#include "WT2605C_Player.h"

#ifdef __AVR__
  #include <SoftwareSerial.h>
  SoftwareSerial SSerial(2, 3); // RX, TX
  #define COMSerial SSerial
  #define ShowSerial Serial

  WT2605C<SoftwareSerial> Mp3Player;
#endif

void setup() {
  ShowSerial.begin(9600);     // Start the hardware serial to communicate with PC
  COMSerial.begin(115200);    // Start software serial for MP3 module
  while (!ShowSerial);        // Wait for the serial monitor to open
  
  ShowSerial.println("Initializing MP3 Player...");
  Mp3Player.init(COMSerial);  // Initialize the MP3 player
  ShowSerial.println("MP3 Player Initialized!");
}

void loop() {
  // Check if there is any incoming data from the Serial Monitor
  if (ShowSerial.available()) {
    String input = ShowSerial.readStringUntil('\n');
    input.trim();  // Remove any whitespace

    if (input.startsWith("index ")) {
      // Command format: index 1
      uint32_t songIndex = input.substring(6).toInt();  // Get the song index after "index "
      ShowSerial.println("Playing song by index: " + String(songIndex));
      Mp3Player.playSDRootSong(songIndex);  // Play the song by index from the SD card root
    }
    else if (input.startsWith("file ")) {
      // Command format: file song.mp3
      String fileName = input.substring(5);  // Get the filename after "file "
      ShowSerial.println("Playing file: " + fileName);
      Mp3Player.playSDSong(fileName.c_str());  // Play the song by filename from the SD card
    }
  }
}
