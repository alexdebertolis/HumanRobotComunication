
import pyaudio
from pydub import AudioSegment
from google.cloud import dialogflow
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2
import serial
import time
import random
from google.protobuf.json_format import MessageToDict
import speech_recognition as sr
import noisereduce as nr
import numpy as np
import wave
import pygame

session_id = '123'  # This can be any unique identifier
language_code = 'en'
project_id= "humanrobot"
credentials = service_account.Credentials.from_service_account_file('/Users/alexdebertolis/Desktop/Human robot + arduino/humanrobot-2f6e43c1a852.json')
 # Create a session client
session_client = dialogflow.SessionsClient(credentials=credentials)
session = session_client.session_path(project_id, session_id)

def dialogflow_client():
    return dialogflow.IntentsClient(credentials=credentials)

def get_agent_path(project_id):
    client = dialogflow.AgentsClient(credentials=credentials)
    return client.agent_path(project_id)


        

# ------------------- GETTER FUNCTIONS ------------------- #

# Get all intents
def list_intents(project_id):
    client = dialogflow.IntentsClient(credentials=credentials)
    parent = get_agent_path(project_id)
    intents = client.list_intents(request={"parent": parent, "intent_view":dialogflow.IntentView.INTENT_VIEW_FULL})
    intList=[]
    for intent in intents:
        intList.append(intent)
        print(f"Intent Name: {intent.name}, Display Name: {intent.display_name}")
    return intList

# Get a specific intent by ID
def get_intent(project_id, intent_id, language_code='en'):
    client = dialogflow.IntentsClient()
    intent_path = client.intent_path(project_id, intent_id)
    intent = client.get_intent(request={"name": intent_path, "language_code": language_code, "intent_view":dialogflow.IntentView.INTENT_VIEW_FULL,})

    print(f"Intent Name: {intent.name}")
    print(f"Display Name: {intent.display_name}")
    print( intent)
    for tp in intent.training_phrases:
        phrase = ''.join([part.text for part in tp.parts])
        print(f"  - {phrase}")
    print("Responses:")
    for message in intent.messages:
        for text in message.text.text:
            print(f"  - {text}")
    return intent

def get_intent_contexts(intent_full_name, language_code='en'):
    client = dialogflow.IntentsClient()
    intent = client.get_intent(request={"name": intent_full_name, "language_code": language_code})
    
    print(f"Intent Name: {intent.display_name}")
    print("Input Contexts:")
    for context in intent.input_context_names:
        print(f"  - {context}")
    print("Output Contexts:")
    for context in intent.output_contexts:
        print(f"  - {context.name} (lifespan: {context.lifespan_count})")

# Get all entity types
def list_entity_types(project_id):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    parent = get_agent_path(project_id)
    entity_types = client.list_entity_types(request={"parent": parent})
    entTypeList= []
    for entity_type in entity_types:
        entTypeList.append(entity_type)
        print(f"Entity Type Name: {entity_type.name}, Display Name: {entity_type.display_name}")
    return entTypeList

# Get a specific entity type by ID
def get_entity_type(project_id, entity_type_id):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    entity_type = client.get_entity_type(request={"name": entity_type_path})
    
    print(f"Entity Type Name: {entity_type.name}, Display Name: {entity_type.display_name}")
    print("Entities:")
    for entity in entity_type.entities:
        print(f"  Value: {entity.value}, Synonyms: {entity.synonyms}")

# Get all entities in a specific entity type
def list_entities_in_entity_type(project_id, entity_type_id):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    entity_type = client.get_entity_type(request={"name": entity_type_path})
    
    for entity in entity_type.entities:
        print(f"Entity Value: {entity.value}, Synonyms: {entity.synonyms}")


# ------------------- Detection ------------------- #




   
def detect_text_intent_with_sentiment_and_act(project_id, session_id, text, language_code, actionMap, **kwargs):
    """
    Detects intent and sentiment from text using Dialogflow, and performs
    the corresponding action based on the provided intent-action mapping.

    Parameters:
    - project_id: Google Cloud project ID.
    - session_id: Unique identifier for the session.
    - text: Text input from which to detect intent.
    - language_code: The language code of the Dialogflow agent (e.g., 'en').
    - action_map: A dictionary mapping intent names to action functions.
    - **kwargs: Additional arguments for actions (e.g., serial connection).
    """
    # Initialize the Dialogflow session client
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    # Prepare the text input for Dialogflow
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    # Set the query parameters with sentiment analysis
    query_params = dialogflow.QueryParameters(
        sentiment_analysis_request_config=dialogflow.SentimentAnalysisRequestConfig(
            analyze_query_text_sentiment=True
        )
    )

    # Create the DetectIntentRequest
    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=query_input,
        query_params=query_params
    )

    # Detect the intent
    response = session_client.detect_intent(request=request)

    # Extract query result and sentiment
    query_result = response.query_result
    intent_name = query_result.intent.display_name
    fulfillment_text = query_result.fulfillment_text
    parameters = dict(query_result.parameters)
    sentiment = query_result.sentiment_analysis_result.query_text_sentiment
    sentiment_level=""
    
    inp_context= query_result.intent.input_context_names
    out_context= query_result.intent.output_contexts
    

   

    # Log the detected intent, fulfillment, and sentiment
    print(f"Query Text: {text}")
    print(f"Detected Intent: {intent_name} (Confidence: {query_result.intent_detection_confidence})")
    print(f"Fulfillment Text: {fulfillment_text}")
    print(f"Sentiment Score: {sentiment.score, }, Magnitude: {sentiment.magnitude}")
    sentiment_level=""
    if sentiment.score <= -0.6:
        sentiment_level="Very Negative"
       
    elif sentiment.score <= -0.2:
        sentiment_level="Negative"
     
    elif sentiment.score <= 0.2:
        sentiment_level="Neutral"
       
    elif sentiment.score <= 0.6:
        sentiment_level="Positive"
        
    else:
        sentiment_level="Positive"
    
    print("sentiment level:"+ sentiment_level)
    print(f"Inpunt Contexts: {inp_context} Output Contexts: {out_context}" )

    if intent_name == "emotion_happy" :
        send_command(ser,"I","1")
        play_sound_for_intent(intent_name)
        time.sleep(3.5)
        play_sound_for_intent("look")
        time.sleep(0.75)
        play_sound_for_intent("look")
    elif intent_name == "emotion_confused" :
        send_command(ser,"I","2")
        play_sound_for_intent(intent_name)
        time.sleep(3.5)
        play_sound_for_intent("look")
        time.sleep(0.75)
        play_sound_for_intent("look")
    elif intent_name == "user_understand_suggestion":

        send_command(ser,"I","3")
        time.sleep(0.5)
        play_sound_for_intent("your_turn")

    elif intent_name == "user_dont_want_suggestion":
        send_command(ser,"I","0")
        time.sleep(1)
        play_sound_for_intent(intent_name)

    
    

    
def audio_input():


    mic_index = 2  # Index of the microphone you want to use
    recognizer = sr.Recognizer()

    with sr.Microphone(device_index=mic_index) as source:
        print("Adjusting for ambient noise, please wait a few seconds...")
        recognizer.adjust_for_ambient_noise(source, duration=2)  # Increase adjustment time
        print("Say something now:")

        # Capture the audio
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        print("Audio captured. Duration:", len(audio.get_raw_data()) / source.SAMPLE_RATE, "seconds")

        # Convert audio to a raw format (array of numbers)
        audio_data = np.frombuffer(audio.get_raw_data(), np.int16)

        # Apply noise reduction
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=source.SAMPLE_RATE)

        # Save the reduced noise audio to a .wav file for debugging
        with wave.open("reduced_audio.wav", "wb") as f:
            f.setnchannels(1)  # Stereo: 2, Mono: 1
            f.setsampwidth(2)  # Sample size in bytes
            f.setframerate(source.SAMPLE_RATE)
            f.writeframes(reduced_noise_audio.tobytes())  # Convert the array to bytes and save it

        try:
            # Use recognizer to convert the audio to text
            text = recognizer.recognize_google(audio, language=language_code)
            print("Transcription: " + text)
            

            # Process the recognized text for intent detection
            detect_text_intent_with_sentiment_and_act(project_id,session_id,text,language_code,audio_files,ser=ser)
           
        

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

def convert_audio_to_mono(input_audio_path, output_audio_path):
    """
    Converts a stereo audio file to mono using pydub.
    
    Parameters:
    - input_audio_path: Path to the input audio file (stereo).
    - output_audio_path: Path where the output mono audio file will be saved.
    """
    audio = AudioSegment.from_wav(input_audio_path)
    mono_audio = audio.set_channels(1)  # Convert to mono
    mono_audio.export(output_audio_path, format="wav")
    print(f"Audio file {input_audio_path} converted to mono and saved as {output_audio_path}")

def play_sound_for_intent(intent_name):
    """ Play sound based on the given intent name. """
    # Check if the intent name is in the dictionary
    if intent_name in audio_files:
        # Get the filename from the dictionary
        filename = audio_files[intent_name]
        try:
            # Load and play the sound file
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
                pygame.time.Clock().tick(10)
            print(f"Played sound for intent: {intent_name}")
        except Exception as e:
            print(f"Failed to play sound: {e}")
    else:
        print(f"No audio file mapped for intent: {intent_name}")



     # ------------------- Arduino Connections------------------- #       
def connect_to_arduino(port, baudrate=9600, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Wait for the connection to establish
        print(f"Connected to Arduino on port {port}")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e}")
        return None

def send_command(ser, command_type, command):
    if ser:
        try:
            # Prepare the command with the correct format and a newline character
            command = f"{command_type}{command}\n"
            # Send the command to the Arduino
            ser.write(command.encode())
            print("Sent command to Arduino:", command.strip())
            # Allow some time for the Arduino to respond
            time.sleep(0.5)
            # Read all lines that Arduino has sent in response
            while ser.in_waiting:
                try:
                    line = ser.readline()
                    # Attempt to decode the line with UTF-8 encoding
                    response = line.decode('utf-8').strip()
                    print("Arduino responds:", response)
                except UnicodeDecodeError:
                    # Handle the case where decoding fails
                    response = line.decode('latin1').strip()
                    print("Decoding error, Arduino response (latin1):", response)
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
    else:
        print("Serial connection not established.")

# ------------------- Actions ------------------- #


def list_audio_devices():
    p = pyaudio.PyAudio()
    print("Listing all audio devices:")
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        print(f"Index: {device_info['index']} - Name: {device_info['name']}")


# ------------------- Example Usage ------------------- #

if __name__ == "__main__":


    audio_files = {
        "emotion_confused": "/Users/alexdebertolis/Desktop/robot audio mp32/001.mp3",
        "emotion_fear": "/Users/alexdebertolis/Desktop/robot audio mp32/002.mp3",
        "emotion_happy": "/Users/alexdebertolis/Desktop/robot audio mp32/003.mp3",
        "user_understand_suggestion": "/Users/alexdebertolis/Desktop/robot audio mp32/003.mp3",
        "emotion_try_again": "/Users/alexdebertolis/Desktop/robot audio mp32/005.mp3",
        "emotion_realization": "/Users/alexdebertolis/Desktop/robot audio mp32/006.mp3",
        "emotion_sad": "/Users/alexdebertolis/Desktop/robot audio mp32/007.mp3",
        "emotion_correct": "/Users/alexdebertolis/Desktop/robot audio mp32/008.mp3",
        "user_dont_want_suggestion": "/Users/alexdebertolis/Desktop/robot audio mp32/011.mp3",
        "user_dont_want_play1": "/Users/alexdebertolis/Desktop/robot audio mp32/011.mp3",
        "songs": "/Users/alexdebertolis/Desktop/robot audio mp32/010.mp3",
        "oona": "/Users/alexdebertolis/Desktop/robot audio mp32/013.mp3",
        "look": "/Users/alexdebertolis/Desktop/robot audio mp32/017.mp3",
        "your_turn": "/Users/alexdebertolis/Desktop/robot audio mp32/018.mp3"
    }

        
    arduino_port = '/dev/cu.usbmodem1412301'  # For Mac/Linux
    # arduino_port = 'COM3'  # For Windows
    

    ser = connect_to_arduino(arduino_port)
    pygame.mixer.init()
    
    while True:
        user_input = input("Enter command or 'exit' to quit: ")
        if user_input == "exit":
            break
        if user_input == "1" :
            audio_input()
        if user_input == "2": 
            send_command(ser,"I","1")
            play_sound_for_intent("emotion_happy")
            time.sleep(3.5)
            play_sound_for_intent("look")
            time.sleep(0.75)
            play_sound_for_intent("look")
        if user_input == "3":
            send_command(ser,"I","3" )
            time.sleep(1.5)
            play_sound_for_intent("your_turn")
        if user_input == "4":
            play_sound_for_intent("emotion_correct")
        if user_input == "5":
            play_sound_for_intent("emotion_try_again")
        if user_input == "6":
            play_sound_for_intent("emotion_realization")
            time.sleep(4)
            play_sound_for_intent("look")
            time.sleep(0.75)
            play_sound_for_intent("look")

        if user_input == "7":
            play_sound_for_intent("oona")
        if user_input == "0":
            send_command(ser, "I", "0")
            time.sleep(1)
            play_sound_for_intent("user_dont_want_suggestion")
        if user_input == "8":
            play_sound_for_intent("your_turn")
        if user_input =="9":
            send_command(ser, "I", "9")
            play_sound_for_intent("songs")
