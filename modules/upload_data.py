import os
import boto3
import shutil
import logging
from dotenv import load_dotenv
from datetime import datetime
from modules.log_initialise import setup_logger

def upload_to_s3(aws_access_key:str, aws_secret_key:str, aws_bucket_name:str, loadDir:str):
    """_summary_

    Args:
        aws_access_key (str): AWS access key
        aws_secret_key (str): AWS secret key
        aws_bucket_name (str): AWS bucket name
        loadDir (str): where to load the data from, to be uploaded to s3
    """

    logger = logging.getLogger(__name__)

    # Initialise s3 client
    s3_client = boto3.client('s3',
                    aws_access_key_id = aws_access_key,
                    aws_secret_access_key = aws_secret_key
                    )

    #Upload data to s3 bucket
    dataFilenames = os.listdir(f'{loadDir}')

    for file in dataFilenames:
        filepath = f'{loadDir}/{file}'
        try:
            s3_client.upload_file(filepath, aws_bucket_name, file)
            print(f'{file} successfully uploaded.')
            logger.info(f'{file} successfully uploaded.')
        except Exception as e:
            print(f'An error has occurred: {e}')
            logger.error(f'{file} failed to upload: {e}')
    print(f'All files from {loadDir} have been uploaded. Deleting directory.')
    logger.info(f'All files from {loadDir} have been uploaded. Directory deleted.')
    shutil.rmtree(loadDir) # Remove the entire directory after all files have been successfully uploaded
    print('UPLOAD COMPLETE.')