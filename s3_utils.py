import boto3
import json

def generate_filename(conversation_memory):
    return f"conversation_{conversation_memory.conversation_id}.json"

def upload_conversation_to_s3(conversation_memory, bucket_name):
    s3_client = boto3.client('s3')
    filename = generate_filename(conversation_memory)
    json_data = conversation_memory.to_json()
    try:
        s3_client.put_object(Bucket=bucket_name, Key=filename, Body=json_data)
        print(f"Conversation uploaded to S3 with filename: {filename}")
        # Return the S3 file location
        return f"{bucket_name}/{filename}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_s3_file_content(bucket_name, file_key):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error retrieving file from S3: {e}")
        return None
