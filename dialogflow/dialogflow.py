


import os
from google.cloud import dialogflow
from google.oauth2 import service_account
session_id = '123'  # This can be any unique identifier
language_code = 'en-US'
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

import os
from google.cloud import dialogflow_v2 as dialogflow

# Helper function to get the agent path
def get_agent_path(project_id):
    client = dialogflow.AgentsClient()
    return client.agent_path(project_id)

# ------------------- GETTER FUNCTIONS ------------------- #

# Get all intents
def list_intents(project_id):
    client = dialogflow.IntentsClient(credentials=credentials)
    parent = get_agent_path(project_id)
    intents = client.list_intents(request={"parent": parent})
    
    for intent in intents:
        print(f"Intent Name: {intent.name}, Display Name: {intent.display_name}")

# Get a specific intent by ID
def get_intent(project_id, intent_id):
    client = dialogflow.IntentsClient(credentials=credentials)
    intent_path = client.intent_path(project_id, intent_id)
    intent = client.get_intent(request={"name": intent_path})
    
    print(f"Intent Name: {intent.name}, Display Name: {intent.display_name}")
    print(f"Training Phrases: {[tp.parts[0].text for tp in intent.training_phrases]}")

# Get all entity types
def list_entity_types(project_id):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    parent = get_agent_path(project_id)
    entity_types = client.list_entity_types(request={"parent": parent})
    
    for entity_type in entity_types:
        print(f"Entity Type Name: {entity_type.name}, Display Name: {entity_type.display_name}")

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

# ------------------- SETTER FUNCTIONS ------------------- #

# Create an intent
def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    client = dialogflow.IntentsClient(credentials=credentials)
    parent = get_agent_path(project_id)
    training_phrases = []
    
    for training_phrases_part in training_phrases_parts:
        parts = [dialogflow.Intent.TrainingPhrase.Part(text=part) for part in training_phrases_part]
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=parts)
        training_phrases.append(training_phrase)
    
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(display_name=display_name, training_phrases=training_phrases, messages=[message])

    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"Intent {display_name} created: {response.name}")
    return response

# Create an entity type
def create_entity_type(project_id, display_name, kind):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    parent = get_agent_path(project_id)
    entity_type = dialogflow.EntityType(display_name=display_name, kind=kind)
    response = client.create_entity_type(request={"parent": parent, "entity_type": entity_type})
    print(f"Entity Type {display_name} created: {response.name}")
    return response

# Create entities within an entity type
def create_entity(project_id, entity_type_id, entity_value, synonyms):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity = dialogflow.EntityType.Entity(value=entity_value, synonyms=synonyms)
    client.batch_create_entities(
        request={
            "parent": client.entity_type_path(project_id, entity_type_id),
            "entities": [entity],
        }
    )
    print(f"Entity {entity_value} created for Entity Type {entity_type_id}")

# Update an intent
def update_intent(project_id, intent_id, new_display_name, new_training_phrases, new_responses):
    client = dialogflow.IntentsClient(credentials=credentials)
    intent_path = client.intent_path(project_id, intent_id)
    intent = client.get_intent(request={"name": intent_path})
    
    intent.display_name = new_display_name
    intent.training_phrases.clear()

    for phrase in new_training_phrases:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        intent.training_phrases.append(dialogflow.Intent.TrainingPhrase(parts=[part]))

    intent.messages.clear()
    text = dialogflow.Intent.Message.Text(text=new_responses)
    intent.messages.append(dialogflow.Intent.Message(text=text))

    client.update_intent(request={"intent": intent})
    print(f"Intent {intent_id} updated")

# Update an entity type
def update_entity_type(project_id, entity_type_id, new_display_name):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    entity_type = client.get_entity_type(request={"name": entity_type_path})

    entity_type.display_name = new_display_name
    client.update_entity_type(request={"entity_type": entity_type})
    print(f"Entity Type {entity_type_id} updated")

# Delete an intent
def delete_intent(project_id, intent_id):
    client = dialogflow.IntentsClient(credentials=credentials)
    intent_path = client.intent_path(project_id, intent_id)
    client.delete_intent(request={"name": intent_path})
    print(f"Intent {intent_id} deleted")

# Delete an entity type
def delete_entity_type(project_id, entity_type_id):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    client.delete_entity_type(request={"name": entity_type_path})
    print(f"Entity Type {entity_type_id} deleted")

# Delete an entity from an entity type
def delete_entity(project_id, entity_type_id, entity_value):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    client.batch_delete_entities(
        request={
            "parent": entity_type_path,
            "entity_values": [entity_value],
        }
    )
    print(f"Entity {entity_value} deleted from Entity Type {entity_type_id}")

# ------------------- Example Usage ------------------- #

if __name__ == "__main__":
    project_id = 'your-project-id'  # Update with your project ID

    # Getters
    list_intents(project_id)
    get_intent(project_id, "your-intent-id")
    list_entity_types(project_id)
    get_entity_type(project_id, "your-entity-type-id")
    list_entities_in_entity_type(project_id, "your-entity-type-id")

    # Setters
    create_intent(project_id, "New Intent", [["Hello"], ["Hi"]], ["Hello, how can I help?"])
    create_entity_type(project_id, "New_Entity_Type", dialogflow.EntityType.Kind.KIND_MAP)
    create_entity(project_id, "your-entity-type-id", "new_entity_value", ["synonym1", "synonym2"])

    # Updates
    update_intent(project_id, "your-intent-id", "Updated Intent", ["Updated phrase 1"], ["Updated response"])
    update_entity_type(project_id, "your-entity-type-id", "Updated Entity Type")

    # Deletions
    delete_intent(project_id, "your-intent-id")
    delete_entity_type(project_id, "your-entity-type-id")
    delete_entity(project_id, "your-entity-type-id", "new_entity_value")
