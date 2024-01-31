import boto3
import json
import datetime

def generate_filename(conversation_memory):
    return f"conversation_{conversation_memory.conversation_id}.json"

def upload_conversation_to_s3(conversation_memory, bucket_name):
    s3_client = boto3.client('s3')
    filename = generate_filename(conversation_memory)
    json_data = conversation_memory.to_json()
    try:
        s3_client.put_object(Bucket=bucket_name, Key=filename, Body=json_data)
        print(f"Conversation uploaded to S3 with filename: {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
