import boto3
import json

class ConversationMemory:
    def __init__(self, max_tokens=200000):
        self.max_tokens = max_tokens
        self.memory = []
        self.current_token_count = 0

    def estimate_tokens(self, text):
        return len(text.split())

    def update_memory(self, new_line):
        new_line_tokens = self.estimate_tokens(new_line)
        self.memory.append(new_line)
        self.current_token_count += new_line_tokens

        while self.current_token_count > self.max_tokens:
            removed_line = self.memory.pop(0)
            self.current_token_count -= self.estimate_tokens(removed_line)

    def get_current_context(self):
        return "\n".join(self.memory)

# Initialize the ConversationMemory class
conversation_memory = ConversationMemory()

# Initialize the Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

def interact_with_bedrock(formatted_prompt):
    body = json.dumps({
        'prompt': formatted_prompt,
        'max_tokens_to_sample': 2048,
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
        response_text = response_body['completion']  # return the generated text

        return response_text
    except Exception as e:
        return f"An error occurred: {e}"

while True:
    user_input = input("> ")
    # Update conversation memory with the new input
    conversation_memory.update_memory(f"Human: {user_input}")

    # Generate the prompt with current context
    current_context = conversation_memory.get_current_context()
    prompt = f"{current_context}\n\nAssistant:"
    response = interact_with_bedrock(prompt)
    
    print(response)
    # Update conversation memory with the model's response
    conversation_memory.update_memory(f"AI: {response}")


