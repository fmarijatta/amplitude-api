import os
import boto3
import logging
import shutil
from dotenv import load_dotenv
from datetime import datetime

#Load environmental variables
load_dotenv(override = True)

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

#Create variables
timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
logDir = 'log'
os.makedirs(logDir, exist_ok = True)
logFilename = f'{logDir}/load_{timestamp}.log'
loadDir = 'data'

logging.basicConfig(
    filename = logFilename,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

#Create the logger and confirm that it's been successfully set up
logger = logging.getLogger()
logger.info('Logger successfully initialised.')

# Initialise s3 client
s3_client = boto3.client('s3',
                  aws_access_key_id = AWS_ACCESS_KEY,
                  aws_secret_access_key = AWS_SECRET_KEY
                  )

#Upload data to s3 bucket
for dir in os.listdir(loadDir):
    dataFilenames = os.listdir(f'{loadDir}/{dir}')
    for file in dataFilenames:
        filepath = f'{loadDir}/{dir}/{file}'
        try:
            s3_client.upload_file(filepath, AWS_BUCKET_NAME, file)
            print(f'{file} successfully uploaded.')
            logging.info(f'{file} successfully uploaded.')
        except Exception as e:
            print(f'An error has occurred: {e}')
            logging.error(f'{file} failed to upload: {e}')
    print(f'All files from {dir} have been uploaded. Deleting directory...')
    shutil.rmtree(dir) # Remove the entire directory after all files have been successfully uploaded
print('UPLOAD COMPLETE.')
