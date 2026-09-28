import requests
import os
from datetime import timedelta
from datetime import datetime
from dotenv import load_dotenv
import logging
import zipfile
import gzip
import json
import shutil
import boto3
from dotenv import load_dotenv

#Load environmental variables
load_dotenv(override = True)

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

#Choose the date to extract. Either 'yesterday' or input a specific date as a string
chosenDate = '20260922'

if chosenDate == 'yesterday':
    daterange = (datetime.today() - timedelta(days = 1)).strftime('%Y%m%d')
else:
    try:
        datetime.strptime(chosenDate, '%Y%m%d')
        daterange = chosenDate
    except:
        print("The variable chosenDate must be either 'yesterday' or a specific date structured as YYYYMMDD. Please change the variable and try again.")

jsonFilename = datetime.strptime(daterange, '%Y%m%d').strftime('%Y-%m-%d')
# Extract .env variables
load_dotenv(override = True)
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')

# Define API call variables
url = 'https://analytics.eu.amplitude.com/api/2/export'
nAttempts = 10

params = {
    'start': f'{daterange}T00',
    'end': f'{daterange}T23'
    }

# Define save and log directories
timestamp = f'{params['start']}-{params['end']}' #the name of the folder represents the data range

zipDir = f'zip/{timestamp}'
os.makedirs(zipDir, exist_ok = True)
gzipDir = f'{zipDir}/gzip/'
os.makedirs(gzipDir, exist_ok = True)
saveDir = f'data/{timestamp}'
os.makedirs(saveDir, exist_ok = True)
logDir = 'log'
os.makedirs(logDir, exist_ok = True)

zipFilename = f'{zipDir}/amplitude_data_{timestamp}.zip'
logFilename = f'{logDir}/amplitude_extract_log_{timestamp}.log'

# Configure logger
logging.basicConfig(
    filename = logFilename,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO
)
logger = logging.getLogger()
logger.info('Logger successfully initialised.')

#Get all files in bucket
session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
s3 = session.resource('s3')
my_bucket = s3.Bucket(AWS_BUCKET_NAME)
s3_files = []
for obj in my_bucket.objects.all():
    s3file = obj.key
    if s3file.find(jsonFilename) != -1:
        # s3_files.append(obj.key)
        s3_files.append(int(s3file.split('.')[0].split('_')[-1]))

continueFlag = 0
if sorted(s3_files) == list(range(0,24)): 
    print(f'Data for {daterange} is already in the s3 bucket. API call aborted.')
    logging.info('Data for this date is already in the s3 bucket. API call aborted.')
elif s3_files != []:
    print(f'Warning: only partial data for {daterange} exists in s3 bucket. Reattempting API call.')
    logging.warning(f'Warning: only partial data for {daterange} exists in s3 bucket. Reattempting API call.')

    continueFlag = 1
else:
    continueFlag = 1

if continueFlag == 1:
    # Attempt API call
    for i in range (nAttempts):
        response = requests.get(url, params = params, auth = (api_key, secret_key))
        statusCode = response.status_code
        #On success, extract and save data as .json
        if 200 <= statusCode < 300:
            data = response.content
            if len(data) > 0:

                # Encode data as .zip file
                try:
                    with open(zipFilename, 'wb') as zipFile:
                        zipFile.write(data)
                        print('.zip file retrieved. Extracting...')
                        logger.info(f'Master zip file {zipFilename} was successfully saved).')
                except Exception as e:
                    print(f'Fatal error: {e}')
                    logger.error(f'A .zip write error has occurred: {e}')

                # Extract .gz files from saved .zip file to gzip subdirectory
                try:
                    with zipfile.ZipFile(zipFilename, 'r') as myZip:
                        myZip.extractall(gzipDir)
                        print(f'.gz files extracted. Saving...')
                        gzipFolderName = os.listdir(gzipDir)[0]
                        gzipSubDir = f'{gzipDir}/{gzipFolderName}'

                        #Extract each .gz file
                        for filename in os.listdir(gzipSubDir):
                            gzFilename = f'{gzipSubDir}/{filename}'
                            saveFilename = f'{saveDir}/amplitude_data_{filename.split('.')[0].split('#')[0]}.json'

                            #Save each extracted .gz file as .json in the data folder
                            try:
                                with gzip.open(gzFilename, 'rt') as f:
                                    gz_content = f.read() # Read the .gz file
                                    print(gz_content)
                                    try:
                                        with open(saveFilename, 'w') as file:
                                            file.write(gz_content)
                                        logger.info(f'{filename} saved to data folder.')
                                    except Exception as e:
                                        print(f'A .gz write error has occurred: {e}')
                                        logger.error(f'A .gz write error has occurred: {e}')
                            except Exception as e:
                                print(f'A .gz read error has occurred: {e}')
                                logger.error(f'A .gz read error has occurred: {e}')
                except Exception as e:
                    print(f'Error extracting {e}')
            else:
                print(f'The call was successful, but no data were retrieved.')
                logger.info('The call was successful, but no data were retrieved.')
            print(f'.json files have been extracted to {saveDir}.')
            break

        #Unsuccessful status code handling  
        elif statusCode == 400:
            print('The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.')
            logger.error(f'Error {statusCode}: The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.')
            break
        elif statusCode == 404:
            print('No data available for the time range requested.')
            logger.error(f'Error {statusCode}: No data available for the time range requested.')
            break
        elif statusCode == 504:
            print('The amount of data is large causing a timeout. For large amounts of data, use the Amazon S3 destination.')
            logger.error(f'Error {statusCode}: The amount of data is large causing a timeout. For large amounts of data, use the Amazon S3 destination.')
            break
        elif statusCode == 403:
            print('Authentification error. Please check your credentials and try again.')
            break
        elif statusCode < 200:
            print(f'Code {statusCode} encountered on attempt {i}. Retrying...')
            logger.warning(f'Code {statusCode} encountered on attempt {i}. Retrying...')
        else:
            print(f'Error: {statusCode}')
            logger.error(f'Unknown error: {statusCode}')
            break # For unknown 300+ errors, break instead of retrying

    # Remove the zip directory
    shutil.rmtree('zip')