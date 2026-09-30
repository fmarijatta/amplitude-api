import os
from modules.log_initialise import setup_logger
from modules.extract_api import extract_json
from datetime import datetime
from dotenv import load_dotenv

#Choose the date to extract. Either 'yesterday' or input a specific date as a string
chosenDate = '20260918'#

#Define variables
url = 'https://analytics.eu.amplitude.com/api/2/export'
# nAttempts = 15
# delay = 10
saveDir = f'data/{chosenDate}'
logDir = 'log'

#Load environmental variables
load_dotenv(override = True)
AMP_API_KEY = os.getenv('AMP_API_KEY')
AMP_SECRET_KEY = os.getenv('AMP_SECRET_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

#Initialise logger
logger = setup_logger(chosenDate, logDir)
logger.info('Logger successfully initialised.')

#Extract data
extract_json(chosenDate, url, AMP_API_KEY, AMP_SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME, saveDir)






