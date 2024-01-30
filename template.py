import boto3
import json

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)
chat_history = {
    'Human': "Hi",
    'AI': "Hello!"
}
def interact_with_bedrock(formatted_prompt):
    body = json.dumps({
        'prompt': prompt,
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
    full_prompt = input("> ")
    prompt = f"\n\nHuman:{full_prompt}\n\nAssistant:"
    print(interact_with_bedrock(prompt))