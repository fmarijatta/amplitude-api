import requests
import os
from datetime import timedelta
from datetime import datetime
from dotenv import load_dotenv
import logging
import zipfile
import gzip
import json

# Extract .env variables
load_dotenv(override = True)
api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')

# Define API call variables
url = 'https://analytics.eu.amplitude.com/api/2/export'
chosenDate = (datetime.today() - timedelta(days = 1)).strftime('%Y%m%d')

params = {
    'start': f'{chosenDate}T00',
    'end': f'{chosenDate}T23'
    }

# Define save and log directories
timestamp = f'{params['start']}-{params['end']}'

zipDir = f'zip/{timestamp}'
gzipDir = f'{zipDir}/gzip/'
os.makedirs(zipDir, exist_ok = True)
os.makedirs(gzipDir, exist_ok = True)
saveDir = f'data/{timestamp}'
os.makedirs(saveDir, exist_ok = True)
logDir = 'log'
os.makedirs(logDir, exist_ok = True)
zipFilename = f'{zipDir}/amplitude_data_{timestamp}.zip'
logFilename = f'{logDir}/amplitude_log_{timestamp}.json'

# Configure logger
logging.basicConfig(
    filename = logFilename,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO
)
logger = logging.getLogger()
logger.info('Logger successfully initialised.')

# Perform API call
response = requests.get(url, params = params, auth = (api_key, secret_key))
statusCode = response.status_code

#On success, extract and save data as .json
if statusCode == 200:
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
                    print(saveFilename)

                    #Save each extracted .gz file as .json in the data folder
                    try:
                        with gzip.open(gzFilename, 'rt') as f:
                            gz_content = f.read() # Read the .gz file
                            try:
                                with open(saveFilename, 'w') as file:
                                    json.dump(gz_content, file) # Write the .json file
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

#Unsuccessful status code handling  
elif statusCode == 400:
    print('The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.')
    logger.error(f'Error {statusCode}: The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.')
elif statusCode == 404:
    print('No data available for the time range requested.')
    logger.error(f'Error {statusCode}: No data available for the time range requested.')
elif statusCode == 504:
    print('The amount of data is large causing a timeout. For large amounts of data, use the Amazon S3 destination.')
    logger.error(f'Error {statusCode}: The amount of data is large causing a timeout. For large amounts of data, use the Amazon S3 destination.')
else:
    print(f'Error: {statusCode}')
    logger.error(f'Error: {statusCode}')