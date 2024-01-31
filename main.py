import json
import datetime
import boto3
from conversation_memory import ConversationMemory
from s3_utils import upload_to_s3


conversation_memory = ConversationMemory()

"""
Create a boto3 client for the Bedrock runtime API.

Parameters:
  - service_name: The name of the AWS service (bedrock-runtime)
  - region_name: The AWS region to use
"""
bedrock = boto3.client(
    service_name='bedrock-runtime', 
    region_name='us-east-1'
)

def interact_with_bedrock(formatted_prompt):
    """
    Send a prompt to the Bedrock API and return the response.

    Parameters:
      - formatted_prompt: The prompt text to send to Bedrock
    
    Returns:
      - The text response from Bedrock
    """
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

def check_conversation_end(response):
    """
    Check if the conversation has reached a natural end based on keywords.

    Parameters:
      - response: The latest AI response
    
    Returns: 
      - True if end of conversation detected, False otherwise
    """
    # Define conditions for ending the conversation
    farewell_keywords = ['goodbye', 'farewell', 'talk later', 'bye']
    if any(keyword in response.lower() for keyword in farewell_keywords):
        return True
    return False

while True:
    user_input = input("> ")
    conversation_memory.update_memory('Human', user_input)

    current_context = conversation_memory.get_current_context()
    prompt = f"{current_context}\n\nAssistant:"
    response = interact_with_bedrock(prompt)
    
    print(response)
    conversation_memory.update_memory('AI', response)

    if check_conversation_end(response):
        bucket_name = 'genailogs1'  
        object_name = f'conversation_logs/conversation_{datetime.datetime.now().isoformat()}.json'
        conversation_json = conversation_memory.to_json()
        if upload_to_s3(bucket_name, object_name, conversation_json):
            print("Conversation successfully uploaded to S3.")
        else:
            print("Failed to upload conversation to S3.")
        break
