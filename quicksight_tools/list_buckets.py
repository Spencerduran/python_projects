import logging
import boto3
import os
from dotenv import load_dotenv

#load_dotenv()

#ACCESS_KEY = os.getenv('ACCESS_KEY')
#SECRET_KEY = os.getenv('SECRET_KEY')
#SESSION_TOKEN = os.getenv('SESSION_TOKEN')
#
#session = boto3.Session(
#    aws_access_key_id=ACCESS_KEY,
#    aws_secret_access_key=SECRET_KEY,
#    aws_session_token=SESSION_TOKEN
#)

# If you want to use different profile call foobar inside .aws/credentials
mysession = boto3.session.Session(profile_name="uat")

# Afterwards, just declare your AWS client/resource services    
#sqs_resource=mysession.resource("sqs")

# or client 
s3_client=mysession.client("s3")
response = s3_client.list_buckets()

# Output the bucket names
print('Existing buckets:')
for bucket in response['Buckets']:
    print(f'  {bucket["Name"]}')
