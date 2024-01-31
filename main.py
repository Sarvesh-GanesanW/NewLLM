import json
import uuid
import boto3
from conversation_memory import ConversationMemory
from s3_utils import upload_conversation_to_s3
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
def reset_conversation_memory():
    global conversation_memory, conversation_id, user_id
    conversation_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    conversation_memory = ConversationMemory()
    conversation_memory.conversation_id = conversation_id

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


def get_response(user_input):
    conversation_memory.update_memory(conversation_id, user_id, 'Human', user_input)
    current_context = conversation_memory.get_current_context()
    prompt = f"{current_context}\n\nAssistant:"
    response = interact_with_bedrock(prompt)
    return response

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_memory, conversation_id, user_id
    user_input = request.json['user_input']
    response = get_response(user_input)
    conversation_memory.update_memory(conversation_id, user_id, 'AI', response)

    # Save the entire conversation to S3
    bucket_name = "genailogs1"
    upload_conversation_to_s3(conversation_memory, bucket_name)

    return jsonify({'response': response})

@app.route('/new_chat', methods=['POST'])
def new_chat():
    global conversation_memory, conversation_id, user_id

    # Save the current conversation before resetting (if it exists)
    if conversation_memory and len(conversation_memory.memory) > 0:
        bucket_name = "genailogs1"
        upload_conversation_to_s3(conversation_memory, bucket_name)

    reset_conversation_memory()
    return jsonify({'message': 'Conversation reset. Ready for new chat.'})


if __name__ == '__main__':
    reset_conversation_memory()
    app.run(debug=True, port=5001)

    