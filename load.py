import os
import boto3
# from boto3.s3.transfer import S3UploadFailedError
from dotenv import load_dotenv
# from botocore.exceptions import ClientError

load_dotenv(override = True)

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# print(AWS_ACCESS_KEY)
# print(AWS_SECRET_KEY)
# print(AWS_BUCKET_NAME)


s3_client = boto3.client('s3',
                  aws_access_key_id = AWS_ACCESS_KEY,
                  aws_secret_access_key = AWS_SECRET_KEY
                  )

#upload a test file
filepath = 'data/20260923T00-20260923T23/amplitude_data_100011471_2026-09-23_0.json'
uploadFilename = 'test.json'

#Attempt upload
s3_client.upload_file(filepath, AWS_BUCKET_NAME, uploadFilename)
