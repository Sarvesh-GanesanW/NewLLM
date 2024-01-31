import boto3
import pandas as pd
import json

# Configure AWS credentials
session = boto3.Session()

# Create an S3 client
s3 = session.client('s3')

# Specify the S3 bucket name and JSON file path
bucket_name = 'genailogs1'
file_name = 'conversation_7cacbf43-a7e7-41fd-9d63-a7e0da5168ef.json'

# Specify the S3 object and its contents
s3_object = s3.get_object(Bucket=bucket_name, Key=file_name)
s3_object_contents = s3_object['Body']

# Use Pandas to read the JSON contents into a DataFrame
data = json.loads(s3_object_contents.read().decode('utf-8'))
df = pd.DataFrame(data)

print(df)