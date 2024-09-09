


import os
from google.cloud import dialogflow
from google.oauth2 import service_account
session_id = '123'  # This can be any unique identifier
language_code = 'en-US'
project_id= "humanrobot"
credentials = service_account.Credentials.from_service_account_file('/Users/alexdebertolis/Desktop/humanrobot-2f6e43c1a852.json') # your credentials
 # Create a session client
session_client = dialogflow.SessionsClient(credentials=credentials)
session = session_client.session_path(project_id, session_id)

def dialogflow_client():
    return dialogflow.IntentsClient(credentials=credentials)

def get_agent_path(project_id):
    client = dialogflow.AgentsClient(credentials=credentials)
    return client.agent_path(project_id)

def transcribe_audio(audio_path):
   
    
    # Read audio file
    with open(audio_path, 'rb') as audio_file:
        input_audio = audio_file.read()

    # Build the audio config and query input
    audio_config = dialogflow.InputAudioConfig(
        audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
        language_code=language_code
    )
    query_input = dialogflow.QueryInput(audio_config=audio_config)

    # Create the request
    request = dialogflow.DetectIntentRequest(
        session=session,
        query_input=query_input,
        input_audio=input_audio
    )

    # Make the request
    response = session_client.detect_intent(request=request)

    # Get and print the response
    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Confidence:", response.query_result.intent_detection_confidence)
    print("Fulfillment text:", response.query_result.fulfillment_text)

def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient(credentials=credentials)

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(request={"parent": parent, "intent": intent})

    print("Intent created: {}".format(response))

    
    
    
def list_intents(project_id):
    client = dialogflow_client()
    parent = get_agent_path(project_id)
    intents = client.list_intents(request={"parent": parent})
    for intent in intents:
        print(f'Intent Name: {intent.name}, Display Name: {intent.display_name}')

def delete_intent(project_id, intent_id):
    client = dialogflow_client()
    intent_path = client.intent_path(project_id, intent_id)
    client.delete_intent(request={"name": intent_path})
    print(f"Intent {intent_id} deleted")


def create_entity_type(project_id, display_name, kind):
    """Create an entity type with the given display name."""
    entity_types_client = dialogflow.EntityTypesClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    entity_type = dialogflow.EntityType(
        display_name=display_name,
        kind=kind
    )

    response = entity_types_client.create_entity_type(request={"parent": parent, "entity_type": entity_type})

    print("Entity type created: {}".format(response))

def create_entity(project_id, entity_type_id, entity_value, synonyms):
    """Create an entity of the given entity type."""
    entity_types_client = dialogflow.EntityTypesClient()

    entity = dialogflow.EntityType.Entity(value=entity_value, synonyms=synonyms)

    response = entity_types_client.create_entity(request={
        "parent": dialogflow.EntityTypesClient.entity_type_path(project_id, entity_type_id),
        "entity": entity
    })

    print("Entity created: {}".format(response))

def list_entity_types(project_id):
    client = dialogflow.EntityTypesClient()
    parent = get_agent_path(project_id)
    entity_types = client.list_entity_types(request={"parent": parent})
    for entity_type in entity_types:
        print(f'Entity Type Name: {entity_type.name}, Display Name: {entity_type.display_name}')

def delete_entity_type(project_id, entity_type_id):
    client = dialogflow.EntityTypesClient()
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    client.delete_entity_type(request={"name": entity_type_path})
    print(f"Entity Type {entity_type_id} deleted")



# Example usage
list_intents("humanrobot")
audio_file_path = '/Users/alexdebertolis/Desktop/OSR_us_000_0010_8k.wav'  # Audio file path
transcribe_audio(audio_file_path)

