



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




   
def detect_text_intent_with_sentiment_and_act(project_id, session_id, text, language_code, **kwargs):
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
    command_type="S"
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
    

    
def audio_input():


    mic_index = 1  # Index of the microphone you want to use
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
            detect_text_intent_with_sentiment_and_act(project_id,session_id,text,language_code,ser=ser)
           
        

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

def send_command(ser,command_type,command,):
    if ser:
        try:
            kommand =f"{command_type}{command}\n"  # Convert integer to string
            ser.write(kommand.encode())  # Encode and add newline for Arduino to recognize the end
            print("arduino command:  " + kommand)
            response = ser.readlines()
            if response:
                for line in response:
                    res=line.decode().strip()  # Read and decode the response
                    print(f"Arduino says: {res}")
            else:
                print("No response received.")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
    else:
        print("Serial connection not established.")
# ------------------- Actions ------------------- #




# ------------------- Example Usage ------------------- #

if __name__ == "__main__":



    audio_files = {
    "emotion_anger": "001",
    "emotion_confused": "002",
    "emotion_disgust": ["003", "004"],
    "emotion_fear": "005",
    "emotion_happy": ["006", "007"],
    "user_understand_suggestion":["006", "007"],
    "emotion_ops": "008",
    "emotion_realization": "009",
    "emotion_sad": "010",
    "emotion_surprise": "011",
    "emotion_thinking": "012",
    "fallback_responses": ["013", "014", "015", "016", "017", "018"],
    "jokes": ["019", "020", "021", "022", "023", "024", "025"],
    "nana": ["026", "027", "028", "029"],
    "sleep_sounds": "031",
    "songs": "032",
    "angry_robot": "033",
    "stories": ["030", "035", "036", "037", "038", "039", "040", "041"],
    "yawns": ["042", "043"],
    "oona": ["044","045","046","047"]
    }   


    
    arduino_port = '/dev/cu.usbmodem1422301'  # For Mac/Linux
    # arduino_port = 'COM3'  # For Windows

    ser = connect_to_arduino(arduino_port)

    

    
    IntList=list_intents(project_id)
    
    
   
    audio_input()
   

    

    