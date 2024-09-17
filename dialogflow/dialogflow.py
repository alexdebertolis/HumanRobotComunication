


import os
from google.cloud import dialogflow
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2
import serial
import time
from google.protobuf.json_format import MessageToDict

session_id = '123'  # This can be any unique identifier
language_code = 'en-US'
project_id= "humanrobot"
credentials = service_account.Credentials.from_service_account_file('/Users/alexdebertolis/Desktop/Human robot + arduino/humanrobot-2f6e43c1a852.json') #path to your credential file
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
    parent = get_agent_path(project_id)
    
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
    parent = get_agent_path(project_id)

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




def update_intent(
    project_id,
    intent_id,
    new_display_name=None,
    new_training_phrases=None,
    new_responses=None,
    replace_training_phrases=False,
    replace_messages=False,
    language_code='en'
):
    """
    Updates an existing intent with options to modify the display name,
    training phrases, and responses.

    Parameters:
    - project_id: Your Google Cloud project ID.
    - intent_id: The ID of the intent to update.
    - new_display_name: (Optional) The new display name for the intent.
    - new_training_phrases: (Optional) A list of new training phrases to add.
    - new_responses: (Optional) A list of new response messages to add.
    - replace_training_phrases: (Optional) If True, replaces existing training phrases.
      If False, appends new training phrases to existing ones.
    - replace_messages: (Optional) If True, replaces existing messages.
      If False, appends new messages to existing ones.
    - language_code: (Optional) The language code (default is 'en').
    """
    client = dialogflow.IntentsClient()
    intent_path = client.intent_path(project_id, intent_id)
    intent = client.get_intent(request={"name": intent_path, "language_code": language_code})

    update_mask_paths = []

    # Update the display name if provided
    if new_display_name is not None:
        intent.display_name = new_display_name
        update_mask_paths.append('display_name')

    # Update training phrases if provided
    if new_training_phrases is not None:
        if replace_training_phrases:
            # Clear existing training phrases
            intent.training_phrases.clear()
        # Add new training phrases
        for phrase in new_training_phrases:
            part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            intent.training_phrases.append(training_phrase)
        update_mask_paths.append('training_phrases')

    # Update messages if provided
    if new_responses is not None:
        if replace_messages:
            # Clear existing messages
            intent.messages.clear()
        # Add new messages
        for response_text in new_responses:
            text = dialogflow.Intent.Message.Text(text=[response_text])
            message = dialogflow.Intent.Message(text=text)
            intent.messages.append(message)
        update_mask_paths.append('messages')

    if not update_mask_paths:
        print("No updates specified.")
        return

    # Specify the fields to update
    update_mask = field_mask_pb2.FieldMask(paths=update_mask_paths)

    # Update the intent with the specified fields and language code
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )
    print(f"Intent '{intent.display_name}' updated with language code '{language_code}'.")

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
    
def add_training_phrases_to_intent(intent_full_name, new_training_phrases_texts, language_code='en'):
    """
    Adds new training phrases to an existing intent without removing existing ones.

    Parameters:
    - intent_full_name: The full resource name of the intent to update.
    - new_training_phrases_texts: A list of strings representing the new training phrases to add.
    - language_code: The language code (default is 'en').
    """
    client = dialogflow.IntentsClient()

    # Retrieve the existing intent
    intent = client.get_intent(
        request={"name": intent_full_name, "language_code": language_code}
    )

    # Build new training phrases
    new_training_phrases = []
    for text in new_training_phrases_texts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=text)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        new_training_phrases.append(training_phrase)

    # Append new training phrases to existing ones
    intent.training_phrases.extend(new_training_phrases)

    # Prepare the update mask
    update_mask = field_mask_pb2.FieldMask(paths=['training_phrases'])

    # Update the intent
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )

    print(f"Added {len(new_training_phrases_texts)} new training phrases to intent '{intent.display_name}'.")

def add_messages_to_intent(intent_full_name, new_message_texts, language_code='en'):
    """
    Adds new messages to an existing intent without removing existing ones.

    Parameters:
    - intent_full_name: The full resource name of the intent to update.
    - new_message_texts: A list of strings representing the new messages to add.
    - language_code: The language code (default is 'en').
    """
    client = dialogflow.IntentsClient()

    # Retrieve the existing intent
    intent = client.get_intent(
        request={"name": intent_full_name, "language_code": language_code}
    )

    # Build new messages
    new_messages = []
    for text in new_message_texts:
        text_message = dialogflow.Intent.Message.Text(text=[text])
        message = dialogflow.Intent.Message(text=text_message)
        new_messages.append(message)

    # Append new messages to existing ones
    intent.messages.extend(new_messages)

    # Prepare the update mask
    update_mask = field_mask_pb2.FieldMask(paths=['messages'])

    # Update the intent
    client.update_intent(
        request={
            "intent": intent,
            "update_mask": update_mask,
            "language_code": language_code
        }
    )

    print(f"Added {len(new_message_texts)} new messages to intent '{intent.display_name}'.")
# Update an entity type
def update_entity_type(project_id, entity_type_id, new_display_name):
    client = dialogflow.EntityTypesClient(credentials=credentials)
    entity_type_path = client.entity_type_path(project_id, entity_type_id)
    entity_type = client.get_entity_type(request={"name": entity_type_path})

    entity_type.display_name = new_display_name
    client.update_entity_type(request={"entity_type": entity_type})
    print(f"Entity Type {entity_type_id} updated")
    
def update_entity(project_id, entity_type_id, entity_value, new_synonyms, language_code='en'):
    """
    Updates an entity's synonyms in a given entity type.

    Parameters:
    - project_id: Your Google Cloud project ID.
    - entity_type_id: The ID of the entity type containing the entity.
    - entity_value: The value of the entity to update.
    - new_synonyms: A list of new synonyms for the entity.
    - language_code: The language code (default is 'en').
    """
    client = dialogflow.EntityTypesClient()

    # Construct the full path for the entity type
    entity_type_path = client.entity_type_path(project_id, entity_type_id)

    # Retrieve the existing entity type with the specified language code
    entity_type = client.get_entity_type(
        request={"name": entity_type_path, "language_code": language_code}
    )

    # Find and update the entity
    updated = False
    for entity in entity_type.entities:
        if entity.value == entity_value:
            entity.synonyms[:] = new_synonyms  # Update the synonyms
            updated = True
            break

    if not updated:
        print(f"Entity '{entity_value}' not found in Entity Type '{entity_type.display_name}'.")
        return

    # Use batch_update_entities to update the entities
    client.batch_update_entities(
        request={
            "parent": entity_type_path,
            "entities": entity_type.entities,
            "language_code": language_code
        }
    )

    print(f"Entity '{entity_value}' updated with new synonyms: {new_synonyms}")

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

# ------------------- Detection ------------------- #
def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.

    Parameters:
    - project_id: Your Google Cloud project ID.
    - session_id: An identifier for the conversation session.
    - texts: A list of text inputs from the user.
    - language_code: The language code of the agent (e.g., 'en' for English).
    """
    session_client = dialogflow.SessionsClient()

    # Create a session path
    session = session_client.session_path(project_id, session_id)
    print(f"Session path: {session}\n")

    for text in texts:
        # Create a text input object
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        # Create a query input object
        query_input = dialogflow.QueryInput(text=text_input)

        # Detect intent
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        # Display the results
        print("=" * 20)
        print(f"Query text: {response.query_result.query_text}")
        print(f"Detected intent: {response.query_result.intent.display_name} (confidence: {response.query_result.intent_detection_confidence})")
        print(f"Fulfillment text: {response.query_result.fulfillment_text}\n")
        return response.query_result.intent.display_name
        #print(response.query_result)

def detect_intent_with_texttospeech_response(
    project_id, session_id, texts, language_code):
        
    """Returns the result of detect intent with texts as inputs and includes
    the response in an audio format.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session_path))

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        # Set the query parameters with sentiment analysis
        output_audio_config = dialogflow.OutputAudioConfig(
            audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16
        )

        request = dialogflow.DetectIntentRequest(
            session=session_path,
            query_input=query_input,
            output_audio_config=output_audio_config,
        )
        response = session_client.detect_intent(request=request)

        print("=" * 20)
        print("Query text: {}".format(response.query_result.query_text))
        print(
            "Detected intent: {} (confidence: {})\n".format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence,
            )
        )
        print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
        # The response's audio_content is binary.
        with open("output.wav", "wb") as out:
            out.write(response.output_audio)
            print('Audio content written to file "output.wav"')


def detect_intent_and_act(project_id, session_id, text, language_code, action_map, **kwargs):
    """
    Detects the intent of the user's input text using Dialogflow and performs
    the corresponding action based on the provided intent-action mapping.

    Parameters:
    - project_id: Your Google Cloud project ID.
    - session_id: A unique identifier for the session.
    - text: The user's input text.
    - language_code: The language code of the agent (e.g., 'en' for English).
    - action_map: A dictionary mapping intent names to action functions.
    - **kwargs: Additional arguments to pass to action functions (e.g., serial connection).
    """
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    # Create a text input
    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    # Create a query input
    query_input = dialogflow.QueryInput(text=text_input)

    # Detect the intent
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

        # Extract query result
    query_result = response.query_result
    intent_name = query_result.intent.display_name
    fulfillment_text = query_result.fulfillment_text

    # Convert parameters to a dictionary
    parameters = dict(query_result.parameters)

    print(f"User: {text}")
    print(f"Detected intent: {intent_name}")
    print(f"Fulfillment text: {fulfillment_text}")
    print(f"Parameters: {parameters}")

    # Find the action associated with the intent
    action_function = action_map.get(intent_name)

    if action_function:
        # Execute the action function, passing necessary parameters
        action_function(fulfillment_text, parameters, **kwargs)
    else:
        print(f"No action defined for intent '{intent_name}'.")


def transcribe_audio_and_act(project_id, session_id, audio_path, language_code, action_map, **kwargs):
    """
    Transcribes audio to text, detects the intent using Dialogflow, and performs
    the corresponding action based on the provided intent-action mapping.

    Parameters:
    - project_id: Your Google Cloud project ID.
    - session_id: A unique identifier for the session.
    - audio_path: Path to the audio file to be transcribed and processed.
    - language_code: The language code of the agent (e.g., 'en' for English).
    - action_map: A dictionary mapping intent names to action functions.
    - **kwargs: Additional arguments to pass to action functions (e.g., serial connection).
    """

    # Initialize the Dialogflow session client
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    # Read the audio file
    with open(audio_path, 'rb') as audio_file:
        input_audio = audio_file.read()

    # Build the audio config (assuming the audio is WAV, LINEAR16 encoded)
    audio_config = dialogflow.InputAudioConfig(
        audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
        language_code=language_code
    )

    # Create the query input with the audio config
    query_input = dialogflow.QueryInput(audio_config=audio_config)

    # Create the DetectIntentRequest with the audio
    request = dialogflow.DetectIntentRequest(
        session=session,
        query_input=query_input,
        input_audio=input_audio
    )

    # Send the request to Dialogflow
    response = session_client.detect_intent(request=request)

    # Extract query result (transcribed text)
    query_result = response.query_result
    transcribed_text = query_result.query_text
    intent_name = query_result.intent.display_name
    fulfillment_text = query_result.fulfillment_text

    # Convert parameters to a dictionary
    parameters = dict(query_result.parameters)

    # Log the details
    print(f"Transcribed Text: {transcribed_text}")
    print(f"Detected Intent: {intent_name}")
    print(f"Fulfillment Text: {fulfillment_text}")
    print(f"Parameters: {parameters}")

    # Find the action associated with the intent
    action_function = action_map.get(intent_name)

    if action_function:
        # Execute the action function, passing necessary parameters
        action_function(fulfillment_text, parameters, **kwargs)
    else:
        print(f"No action defined for intent '{intent_name}'.")

def transcribe_audio_detect_intent_and_respond(
    project_id, session_id, audio_path, language_code, action_map, **kwargs
):
    """
    Transcribes an audio file to text, detects intent using Dialogflow, performs
    the corresponding action, and generates a response in both text and audio.

    Parameters:
    - project_id: Google Cloud project ID.
    - session_id: Unique identifier for the session.
    - audio_path: Path to the audio file for transcription.
    - language_code: The language code of the Dialogflow agent (e.g., 'en').
    - action_map: A dictionary mapping intent names to action functions.
    - **kwargs: Additional arguments for actions (e.g., serial connection to Arduino).
    """
    # Initialize the Dialogflow session client
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    # Read the audio file
    with open(audio_path, 'rb') as audio_file:
        input_audio = audio_file.read()

    # Audio input configuration for Dialogflow (assuming LINEAR16 WAV format)
    audio_config = dialogflow.InputAudioConfig(
        audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
        language_code=language_code
    )

    # Output audio configuration for TTS response (e.g., OUTPUT_AUDIO_ENCODING_LINEAR_16)
    output_audio_config = dialogflow.OutputAudioConfig(
        audio_encoding=dialogflow.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16
    )

    # Create the DetectIntentRequest with the audio and the output audio config
    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=dialogflow.QueryInput(audio_config=audio_config),
        input_audio=input_audio,
        output_audio_config=output_audio_config
    )

    # Detect the intent
    response = session_client.detect_intent(request=request)

    # Extract query result
    query_result = response.query_result
    transcribed_text = query_result.query_text
    intent_name = query_result.intent.display_name
    fulfillment_text = query_result.fulfillment_text
    parameters = MessageToDict(query_result.parameters)

    # Log the transcribed text, detected intent, and fulfillment text
    print(f"Transcribed Text: {transcribed_text}")
    print(f"Detected Intent: {intent_name}")
    print(f"Fulfillment Text: {fulfillment_text}")
    print(f"Parameters: {parameters}")

    # Perform the action based on the detected intent
    action_function = action_map.get(intent_name)
    if action_function:
        # Execute the corresponding action, passing parameters
        action_function(fulfillment_text, parameters, **kwargs)
    else:
        print(f"No action defined for intent '{intent_name}'.")

    # Save the audio response (output_audio) from Dialogflow as a WAV file
    audio_output_file = "response_output.wav"
    with open(audio_output_file, "wb") as audio_file:
        audio_file.write(response.output_audio)
        print(f'Audio content written to "{audio_output_file}"')

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

def send_command(ser, command):
    if ser:
        ser.write((command + '\n').encode())
        # Read the response from Arduino
        response = ser.readline().decode().strip()
        if response:
            print(f"Arduino says: {response}")
    else:
        print("Serial connection not established.")
# ------------------- Actions ------------------- #

def action_turn_on_light(fulfillment_text, parameters, **kwargs):
    ser = kwargs.get('ser')  # Get the serial connection from kwargs
    send_command(ser, "LED_ON")
    print("Action: Turned on the light.")

def action_turn_off_light(fulfillment_text, parameters, **kwargs):
    ser = kwargs.get('ser')
    send_command(ser, "LED_OFF")
    print("Action: Turned off the light.")
# ------------------- Example Usage ------------------- #

if __name__ == "__main__":

    
    action_map = {
        "turn_on-light": action_turn_on_light,
        "turn-off-lights": action_turn_off_light,
       
    }

    jokes = [
    "Why did the math book look sad? Because it had too many problems!",
    "What do you call cheese that's not yours? Nacho cheese!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the computer go to the doctor? Because it had a virus!",
    "What do you get when you cross a snowman and a shark? Frostbite!",
    "Why did the cookie go to the hospital? Because he felt crummy!",
    "What did one volcano say to the other? I lava you!",
    "Why did the teddy bear say no to dessert? Because she was already stuffed!",
    "How do you make a tissue dance? Put a little boogie in it!",
    "Why did the kid bring a ladder to school? Because he wanted to go to high school!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why are ghosts bad liars? Because you can see right through them!",
    "What kind of tree fits in your hand? A palm tree!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the melon jump into the lake? It wanted to be a watermelon!",
    "What do you get when you cross a fish and an elephant? Swimming trunks!",
    "Why can't Elsa have a balloon? Because she will let it go!",
    "What do you call an alligator in a vest? An investigator!",
    "Why did the picture go to jail? Because it was framed!",
    ]
    stories = [
    "The Little Red Balloon: Once upon a time, a little red balloon floated up into the sky, carrying a child's wish for adventure. As it drifted over mountains and oceans, it collected stories from around the world to bring back home.",
    "The Brave Little Turtle: Tommy the turtle wanted to see the world beyond his pond. One day, he mustered up the courage to explore and discovered that being brave helped him make new friends.",
    "The Magic Paintbrush: Lily found a magic paintbrush that brought her drawings to life. She painted gardens full of flowers and shared them with everyone in her town, spreading joy and color.",
    "The Lost Puppy: Max, a playful puppy, got lost in the city. With the help of some friendly animals, he found his way back home, learning the importance of listening to his parents.",
    "The Friendly Dragon: In a village afraid of dragons, a young girl named Mia befriended a gentle dragon named Spark. Together, they showed everyone that friendship can overcome fear.",
    "The Boy Who Loved Stars: Alex dreamed of touching the stars. Every night, he built a taller and taller ladder. Though he couldn't reach them, he realized that his dreams inspired others to look up and wonder.",
    "The Talking Tree: Deep in the forest stood a tree that could talk. It shared stories of nature's wonders with a group of children, teaching them to appreciate and protect the environment.",
    "The Kind Robot: A robot named Bolt wanted to understand human emotions. By helping people in small ways every day, Bolt learned that kindness is the key to happiness.",
    "The Invisible Cloak: Emma found an invisible cloak that made her unseen. She used it to help others without them knowing, discovering that doing good deeds is its own reward.",
    "The Time-Traveling Sandwich: Jake made a sandwich so delicious that it transported him back in time. He met his grandparents as children and learned valuable lessons about family.",]

    songs = [
    "Twinkle Twinkle Little Star",
    "You Are My Sunshine",
    "Hakuna Matata",  # From The Lion King
    "Let It Go",  # From Frozen
    "The Wheels on the Bus",
    "If You're Happy and You Know It",
    "Baby Shark",
    "Somewhere Over the Rainbow",
    "Can't Stop the Feeling!",  # By Justin Timberlake (from Trolls)
    "How Far I'll Go",  # From Moana
    "Under the Sea",  # From The Little Mermaid
    "A Whole New World",  # From Aladdin
    "Happy",  # By Pharrell Williams
    "Roar",  # By Katy Perry
    "Count on Me",  # By Bruno Mars
    "Try Everything",  # By Shakira (from Zootopia)
    "You've Got a Friend in Me",  # From Toy Story
    "Do-Re-Mi",  # From The Sound of Music
    "What a Wonderful World",  # By Louis Armstrong
    "Three Little Birds",  # By Bob Marley
    ]

    parameter=[{
        'display_name': 'entertainment_type',
        'entity_type_display_name': '@Entertainment_Type',
        'mandatory': True,
        'prompts':["Would you like a joke, a story, or a song?"],
        'default_value' : '',
        'value':'$entertainment_type'
    }]
    arduino_port = '/dev/cu.usbmodem1422101'  # For Mac/Linux
    # arduino_port = 'COM3'  # For Windows

    ser = connect_to_arduino(arduino_port)

    # Send commands to the Arduino
    #send_command(ser, "LED_OFF")

    #IntList=list_intents(project_id)
    #list_entity_types(project_id)
    detect_intent_texts(project_id,session_id,["Hi"], language_code)
    #detect_intent_and_act(project_id,session_id,"can you turn off the light?","en",action_map,ser=ser)
    #update_intent_contexts("projects/humanrobot/agent/intents/e8d84166-a894-42bb-a7ae-13b248877017",project_id,[],[("request_of_entertainment_joke", 2),("request_of_entertainment_story", 2),("request_of_entertainment_song", 2)])
    #update_intent(project_id,"257456c1-1476-4164-8d20-ef65b157690c", "Awaiting Request of Entertainment", ["I want to hear a joke.","Tell me a story.","Sing me a song.","A joke, please.","I'd like a story.","Can you sing?"], ["yeah sure here a $entertainment_type for you:"])
    #detect_intent_with_texttospeech_response(project_id,session_id, ["Tell me a story"], "en")
    #update_intent_parameters("projects/humanrobot/agent/intents/257456c1-1476-4164-8d20-ef65b157690c", [] )
    
    #create_followup_intent_with_input_context(project_id,"Awaiting Request of Entertainment", ["I want to hear a joke.","Tell me a story.","Sing me a song.","A joke, please.","I'd like a story.","Can you sing?"],[], "awaiting_request_of_entertainment", parameter )
    #create_intent(project_id, "turn_on-light", ["Can you turn on the light?", "turn the light on"], ["Sure, i will turn the light on", "Sure here you are"])
    #create_intent(project_id,"turn-off-lights", ["Can you turn the light off", "Turn the light off"], ["Sure boss", "Done"])

    #delete_intent(project_id,"257456c1-1476-4164-8d20-ef65b157690c")
    #get_intent(project_id,"e8d84166-a894-42bb-a7ae-13b248877017")
    #if ser:
    #    ser.close()
    
    
#("request_of_entertainment_joke", 2),("request_of_entertainment_story", 2),("request_of_entertainment_song", 2)
   