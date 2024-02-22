import json
import uuid
import boto3
from conversation_memory import ConversationMemory
from s3_utils import upload_conversation_to_s3, get_s3_file_content
from database_utils import insert_conversation_metadata, get_conversation_metadata, create_conversations_table
from flask import Flask, request, jsonify

# Initialize the ConversationMemory with UUIDs for conversation and user
conversation_id = str(uuid.uuid4())
user_id = str(uuid.uuid4())
conversation_memory = ConversationMemory()

# Initialize the Bedrock client
try:
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
except Exception as e:
    print(f"Error initializing Bedrock client: {e}")

"""Resets the conversation memory by generating new UUIDs for the 
conversation_id and user_id, and initializing a new ConversationMemory 
object.

This allows the conversation state to be reset, while preserving the 
existing ConversationMemory class.
"""
def reset_conversation_memory():
    global conversation_memory, conversation_id, user_id
    # Generate new UUIDs for the conversation and user
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    # Initialize a new ConversationMemory object with the new conversation_id
    conversation_memory = ConversationMemory()
    conversation_memory.conversation_id = conversation_id

"""
interact_with_bedrock sends a prompt to the Bedrock runtime API and returns the text response.

It takes in a formatted prompt string, calls the Bedrock runtime invoke_model API with the prompt and various sampling parameters, 
and returns the text response from Bedrock.

Handles errors from the Bedrock API invocation and returns an error message string on failure.
"""
def interact_with_bedrock(formatted_prompt):
    body = json.dumps({
        'prompt': formatted_prompt,
        'max_tokens_to_sample': 4096,
        'temperature': 0.5,
        'top_p': 0.9,
        'top_k': 300,
        'stop_sequences': ["\n\nHuman:"]
    })
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-v2:1',
            accept='application/json',
            contentType='application/json',
            body=body
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        response_text = response_body['completion']
        return response_text
    except Exception as e:
        return f"An error occurred: {e}"


"""Updates the conversation memory with the user input, retrieves the current 
context from the memory, formats a prompt using the context and a placeholder 
for the assistant's response, interacts with the Bedrock AI model to generate 
a response, and returns the response.
"""
def get_response(user_input):
    conversation_memory.update_memory(conversation_id, user_id, 'Human', user_input)
    current_context = conversation_memory.get_current_context()
    prompt = f"Human: If the current context contains a question related to any procedure related to databases, Greet the user and request the user for a connection name. After you get the connection name, enclose the connection name with double quotes, and use that name as the connection string in the generated response. For connecting to databases, instead of detailing parameters like dbname, user, host, and password, simply specify connection the connection name inside it.\n\n{current_context}\n\nAssistant:"
    response = interact_with_bedrock(prompt)
    return response

app = Flask(__name__)

"""
chat endpoint that handles a user chat input.

- Gets the user input from the request
- Calls get_response() to generate the AI response
- Updates the conversation memory with the user input and AI response
- Saves the entire conversation to S3 after every user interaction
- Returns the AI response
"""
@app.route('/chat', methods=['POST'])
def chat():
    global conversation_memory, conversation_id, user_id
    user_input = request.json['user_input']
    response = get_response(user_input)
    conversation_memory.update_memory(conversation_id, user_id, 'AI', response)

    conversation_name = request.json.get('conversation_name', 'New Chat')

    # Save the entire conversation to S3
    bucket_name = "genailogs1"
    s3_file_location = upload_conversation_to_s3(conversation_memory, bucket_name)
    if s3_file_location:
        print(conversation_id)
        insert_conversation_metadata(conversation_id, user_id, s3_file_location, conversation_name)

    return jsonify({'response': response})


"""
Retrieves a conversation from S3 based on the conversation ID, 
and returns the chat messages from the conversation.

Looks up the metadata for the conversation ID to get the S3 file location. 
Gets the file contents from S3, parses the JSON, and returns the chat messages array.

Returns:
    200 with chat messages array on success
    404 if no conversation found for ID
    500 on error retrieving from S3 or invalid file format
"""
@app.route('/get_conversation', methods=['POST'])
def get_conversation():
    conversation_id = request.args.get('conversation_id')
    
    metadata = get_conversation_metadata(conversation_id)
    if not metadata:
        return jsonify({'error': 'No conversation found'}), 404

    s3_file_location = metadata['s3_file_location'] 
    bucket_name, file_key = s3_file_location.split('/', 1)
    
    file_content = get_s3_file_content(bucket_name, file_key)
    if file_content is None:
        return jsonify({'error': 'Error retrieving conversation from S3'}), 500
    
    try:
        chat_messages = json.loads(file_content) 
    except json.JSONDecodeError: 
        return jsonify({'error': 'Invalid Conversation Format'}), 500
    
    return jsonify({'chat_messages': chat_messages})

"""Saves the current conversation to S3 before resetting the 
conversation memory and returning a response indicating the 
conversation has been reset and is ready for a new chat."""
@app.route('/new_chat', methods=['POST'])
def new_chat():
    global conversation_memory, conversation_id, user_id
    conversation_name = request.json.get('conversation_name', 'New Chat')
    reset_conversation_memory()
    # Save the current conversation before resetting (if it exists)
    if conversation_memory and len(conversation_memory.memory) > 0:
        bucket_name = "genailogs1"
        s3_file_location = upload_conversation_to_s3(conversation_memory, bucket_name)
        if s3_file_location:
            print(conversation_id)
            # Insert metadata with the current conversation_id before it gets reset
            insert_conversation_metadata(conversation_id, user_id, s3_file_location, conversation_name)

    # Reset the conversation memory which will also generate a new conversation_id
    return jsonify({'message': 'Conversation reset. Ready for new chat.'})

import socket
from contextlib import closing

"""Checks if a given port is available for use.

Args:
    port: The port number to check.

Returns: 
    True if the port is available, False otherwise.
"""
def check_port(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex(('0.0.0.0', port)) == 0:
            return False
        else:
            return True
        
if __name__ == '__main__':
    port = 5000
    while True:
        if check_port(port):
            reset_conversation_memory()
            create_conversations_table()
            app.run(port=port, debug=True)
            break
        else:
            port += 1
