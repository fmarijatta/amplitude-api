import os
import boto3
import shutil
from dotenv import load_dotenv
from datetime import datetime
from modules.log_initialise import setup_logger

def upload_to_s3(aws_access_key, aws_secret_key, aws_bucket_name, loadDir):
    logger = setup_logger(__name__)

    # Initialise s3 client
    s3_client = boto3.client('s3',
                    aws_access_key_id = aws_access_key,
                    aws_secret_access_key = aws_secret_key
                    )

    #Upload data to s3 bucket
    for dir in os.listdir(loadDir):
        dataFilenames = os.listdir(f'{loadDir}/{dir}')
        for file in dataFilenames:
            filepath = f'{loadDir}/{dir}/{file}'
            try:
                s3_client.upload_file(filepath, aws_bucket_name, file)
                print(f'{file} successfully uploaded.')
                logger.info(f'{file} successfully uploaded.')
            except Exception as e:
                print(f'An error has occurred: {e}')
                logger.error(f'{file} failed to upload: {e}')
        print(f'All files from {dir} have been uploaded. Deleting directory.')
        logger.info(f'All files from {dir} have been uploaded. Directory deleted.')
        shutil.rmtree(dir) # Remove the entire directory after all files have been successfully uploaded
    print('UPLOAD COMPLETE.')