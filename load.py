import os
import boto3
# from boto3.s3.transfer import S3UploadFailedError
from dotenv import load_dotenv
# from botocore.exceptions import ClientError

#Load environmental variables
load_dotenv(override = True)

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

#Create variables
loadDir = 'data'

#Initialise s3 client
s3_client = boto3.client('s3',
                  aws_access_key_id = AWS_ACCESS_KEY,
                  aws_secret_access_key = AWS_SECRET_KEY
                  )

#upload a test file
# filepath = 'data/20260923T00-20260923T23/amplitude_data_100011471_2026-09-23_0.json'
# uploadFilename = 'test.json'

# #Attempt upload
# s3_client.upload_file(filepath, AWS_BUCKET_NAME, uploadFilename)

dataDirs = os.listdir(loadDir)
for dir in dataDirs:
    dataFilenames = os.listdir(f'{loadDir}/{dir}')
    for file in dataFilenames:
        filepath = f'{loadDir}/{dir}/{file}'
        print(filepath)
        try:
            #Attempt upload
            s3_client.upload_file(filepath, AWS_BUCKET_NAME, file)
        except Exception as e:
            print(f'An error has occurred: {e}')



