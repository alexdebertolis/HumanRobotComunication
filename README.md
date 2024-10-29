Interactive Game with Oona Robot
==============================================================

This GitHub repository documents an Arduino-based interactive game featuring "Oona," a robot that interacts with users through visual and auditory signals. The project uses Arduino for controlling hardware components like servos, LEDs, and audio outputs, paired with a Python script integrating Dialogflow for advanced user interaction capabilities.

Overview
--------

The project integrates several hardware components such as the HUSKYLENS for face recognition, a LED matrix for displaying visual cues, and servos for physical movements. The game logic includes multiple sequences where Oona interacts with the player, reacting differently based on the player's actions and the game's state.

Interaction Flow
----------------

The interaction with Oona is defined in two main phases: Initial Interaction and Game Play.

### Initial Interaction

1.  **First Approach**: When Oona is activated, it wakes up and uses the camera to look for user interaction. If the user greets Oona with a "Hello," Oona transitions to a happy state; otherwise, it enters a waiting loop or shows confusion based on the absence or misrecognition of interaction.
    
    *   **Oona Happy**: Responds with nodding and a happy sound.
        
    *   **Oona Confused**: Moves into a confused state if no proper interaction is detected.
        
2.  **Suggestion Phase**: After initial interaction, Oona suggests playing a game by showing a dice icon on the LED matrix and playing suggestive sounds. Depending on the user's response, Oona can start the game, go to sleep, or show further confusion.
    

### Game Play

1.  **Tutorial**: The game begins with a tutorial showing the user how to interact with the game, demonstrated through both visual and auditory instructions.
    
2.  **Game Sequences**: The game includes multiple levels of difficulty, each requiring the user to respond correctly to Oona's cues:
    
    *   **Easy**: Simple sequences signaled by LED colors.
        
    *   **Medium and Hard**: Progressively more complex sequences requiring quicker responses.
        
3.  **End Game**: Oona reacts joyously if the game completes successfully or encourages retrying if the user fails.
    

Interaction via Dialogflow
--------------------------

The interactions are enhanced by a Python script that integrates Dialogflow, enabling sophisticated voice command processing and dynamic responses based on user inputs. This setup allows Oona to understand and react to a broader array of commands and queries, making the game more engaging and interactive.

Dependencies
------------

*   Arduino IDE
    
*   Python 3
    
*   Libraries: HUSKYLENS, Adafruit\_NeoPixel, etc.
    
*   Dialogflow API
    

Installation
------------

Instructions to set up the hardware, compile the Arduino sketch, deploy it to the microcontroller, and run the Dialogflow integrated Python script for handling complex interactions.

Contributing
------------

Details on how to contribute to the project, report issues, and submit pull requests are provided, encouraging collaboration and improvements from the community.
