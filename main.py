import os
from modules.log_initialise import setup_logger
from modules.extract_api import extract_json
from modules. upload_data import upload_to_s3
from datetime import datetime
from dotenv import load_dotenv

#Load environmental variables
load_dotenv(override = True)
AMP_API_KEY = os.getenv('AMP_API_KEY')
AMP_SECRET_KEY = os.getenv('AMP_SECRET_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

chosenDate = 'yesterday' if os.getenv('chosenDate') == None else os.getenv('chosenDate')

#Define variables
url = 'https://analytics.eu.amplitude.com/api/2/export'
# nAttempts = 15
# delay = 10
dataDir = f'data/{chosenDate}'
logDir = 'log'

#Initialise logger
logger = setup_logger(chosenDate, logDir)
logger.info('Logger successfully initialised.')

#Extract data
extract_json(chosenDate, url, AMP_API_KEY, AMP_SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME, dataDir)

#Upload data to s3
upload_to_s3(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME, dataDir)






