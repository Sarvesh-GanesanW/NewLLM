import boto3
import json

"""Generates a filename for storing a Conversation memory object in S3.

The filename is generated based on the conversation_id property of the 
Conversation memory object, with a .json extension.
"""
def generate_filename(conversation_memory):
    return f"conversation_{conversation_memory.conversation_id}.json"

"""Uploads a Conversation memory object to S3.

Generates a filename based on the conversation ID, converts the 
Conversation object to JSON, uploads it to the provided S3 bucket,
and returns the S3 file location if successful or None if there was an error.
"""
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

"""Retrieves the content of an S3 object and returns it as a string.

Args:
    bucket_name: The name of the S3 bucket.
    file_key: The key of the S3 object to retrieve.

Returns:
    The content of the S3 object as a string, or None if there was an error.
"""
def get_s3_file_content(bucket_name, file_key):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Error retrieving file from S3: {e}")
        return None
