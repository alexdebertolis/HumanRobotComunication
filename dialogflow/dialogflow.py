


import os
from google.cloud import dialogflow
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2
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

def create_intent_with_contexts(
    project_id,
    display_name,
    training_phrases_parts,
    message_texts,
    input_context_names=[],
    output_contexts=[],
    parameters=[],
    is_fallback=False
):
    client = dialogflow.IntentsClient()
    parent = client.agent_path(project_id)
    
    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)
    
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    
    # Prepare contexts
    input_contexts_full = [f"projects/{project_id}/agent/sessions/-/contexts/{context}" for context in input_context_names]
    output_contexts_full = [
        dialogflow.Context(
            name=f"projects/{project_id}/agent/sessions/-/contexts/{context}",
            lifespan_count=lifespan
        )
        for context, lifespan in output_contexts
    ]

     # Prepare parameters
    intent_parameters = []
    for param in parameters:
        parameter = dialogflow.Intent.Parameter(
            display_name=param['display_name'],
            entity_type_display_name=param['entity_type_display_name'],
            mandatory=param.get('mandatory', False),
            prompts=param.get('prompts', []),
            default_value=param.get('default_value', ''),
            value=param.get('value', f"${{{param['display_name']}}}")
        )
        intent_parameters.append(parameter)
    
    # Create intent
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
        input_context_names=input_contexts_full,
        output_contexts=output_contexts_full,
        parameters=parameters,
        is_fallback=is_fallback
    )
    
    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"Intent '{display_name}' created: {response.name}")
    return response
def create_followup_intent_with_input_context(
    project_id,
    display_name,
    training_phrases_parts,
    message_texts,
    input_context_name,
    parameters=[]
):
    client = dialogflow.IntentsClient()
    parent = client.agent_path(project_id)

    # Create training phrases
    training_phrases = []
    for phrase in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    # Create the message
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    # Set the input context
    input_context = f"projects/{project_id}/agent/sessions/-/contexts/{input_context_name}"

    # Create the intent
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
        input_context_names=[input_context],
        parameters=parameters
    )

    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"Follow-up intent '{display_name}' created: {response.name}")
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




def update_intent(project_id, intent_id, new_display_name, new_training_phrases, new_responses, language_code='en'):
    client = dialogflow.IntentsClient()
    intent_path = client.intent_path(project_id, intent_id)
    intent = client.get_intent(request={"name": intent_path, "language_code": language_code})

    # Update the display name
    intent.display_name = new_display_name

    # Clear existing training phrases and add new ones
    intent.training_phrases.clear()
    for phrase in new_training_phrases:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        intent.training_phrases.append(training_phrase)

    # Clear existing messages and add new ones
    intent.messages.clear()
    # Ensure new_responses is a list of strings
    text = dialogflow.Intent.Message.Text(text=new_responses)
    message = dialogflow.Intent.Message(text=text)
    intent.messages.append(message)

    # Specify the fields to update
    update_mask = field_mask_pb2.FieldMask(paths=['display_name', 'training_phrases', 'messages'])

    # Update the intent with the specified fields and language code
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )
    print(f"Intent {intent_id} updated with language code '{language_code}'")

def update_intent_contexts(intent_full_name, project_id, input_context_ids, output_contexts_info, language_code='en'):
    client = dialogflow.IntentsClient()
    
    # Retrieve the existing intent
    intent = client.get_intent(request={"name": intent_full_name, "language_code": language_code})

    # Update input contexts
    intent.input_context_names.clear()
    for context_id in input_context_ids:
        context_name = f"projects/{project_id}/agent/sessions/-/contexts/{context_id}"
        intent.input_context_names.append(context_name)

    # Update output contexts using dialogflow.Context
    intent.output_contexts.clear()
    for context_id, lifespan in output_contexts_info:
        context_name = f"projects/{project_id}/agent/sessions/-/contexts/{context_id}"
        output_context = dialogflow.Context(
            name=context_name,
            lifespan_count=lifespan
        )
        intent.output_contexts.append(output_context)

    # Prepare update mask to update only contexts
    update_mask = field_mask_pb2.FieldMask(paths=['input_context_names', 'output_contexts'])

    # Update intent with the updated contexts
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )
    print(f"Intent '{intent.display_name}' updated with new contexts.")

def update_intent_parameters(intent_full_name, parameters, language_code='en'):
    client = dialogflow.IntentsClient()
    intent = client.get_intent(request={"name": intent_full_name, "language_code": language_code})

    # Update parameters
    intent.parameters.clear()
    for param in parameters:
        parameter = dialogflow.Intent.Parameter(
            display_name=param['display_name'],
            entity_type_display_name=param['entity_type_display_name'],
            mandatory=param.get('mandatory', False),
            prompts=param.get('prompts', []),
            default_value=param.get('default_value', ''),
            value=param.get('value', f"${{{param['display_name']}}}")
        )
        intent.parameters.append(parameter)

    # Prepare update mask
    from google.protobuf import field_mask_pb2
    update_mask = field_mask_pb2.FieldMask(paths=['parameters'])

    # Update the intent
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )
    print(f"Parameters updated for intent '{intent.display_name}'.")

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
    project_id = 'humanrobot'  # Update with your project ID

    # Getters
    IntList=list_intents(project_id)
    get_intent(project_id,"523db2c8-b27d-4249-8b5f-6f5f0593f40c", "en")
   

'''update_intent(
    project_id,
    "e8d84166-a894-42bb-a7ae-13b248877017",
    "Default Welcome Intent",
    ["Hello!", "Hi robot!", "Hey, what can you do?", "Hello, I’m here!"],
    [
        "Hi there! I’m here to entertain and help you feel better! What would you like to do today?",
        "Hello! How can I make your day more fun?",
        "Hi! How are you doing?",
        "Good day! What can I do for you today?"
    ],
    language_code='en'  )'''
    

   