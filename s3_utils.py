import boto3

def upload_to_s3(bucket_name, object_name, conversation_data):
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(Body=conversation_data, Bucket=bucket_name, Key=object_name)
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False
