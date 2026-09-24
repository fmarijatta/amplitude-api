import requests
import os
from datetime import timedelta
from datetime import datetime
from dotenv import load_dotenv
import logging
import zipfile
import gzip
import json

#Extract .env variables
load_dotenv(override = True)

api_key = os.getenv('AMP_API_KEY')
secret_key = os.getenv('AMP_SECRET_KEY')

#Define variables
url = 'https://analytics.eu.amplitude.com/api/2/export'
yesterdayDate = (datetime.today() - timedelta(days = 1)).strftime('%Y%m%d')

timestamp = datetime.now().strftime('%Y%m%dT00')
params = {
    'start': f'{yesterdayDate}T00',
    'end': f'{yesterdayDate}T23'
    }

#define save and log dirs
timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

saveDir = f'data/{timestamp}'
os.makedirs(saveDir, exist_ok = True)

logDir = 'log'
os.makedirs(logDir, exist_ok = True)

zipDir = f'zip/{timestamp}'
gzipDir = f'{zipDir}/gzip/'
os.makedirs(zipDir, exist_ok = True)
os.makedirs(gzipDir, exist_ok = True)

zipFilename = f'{zipDir}/amplitude_data_{timestamp}.zip'
logFilename = f'{logDir}/amplitude_log_{timestamp}.json'

#Configure logs
logging.basicConfig(
    filename = logFilename,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

#Create the logger and confirm that it's been successfully set up
logger = logging.getLogger()
logger.info('Logger successfully initialised.')

#get data
response = requests.get(url, params = params, auth = (api_key, secret_key))
statusCode = response.status_code

if statusCode == 200:
    data = response.content
    if len(data) > 0:
        try:
            with open(zipFilename, 'wb') as zipFile:
                zipFile.write(data)
                # print('.zip file retrieved. Extracting...')
                # logger.info(f'Master zip file {filename} was successfully saved).')
        except Exception as e:
            print(f'Fatal error: {e}')
            logger.error(f'Error {statusCode}: A write error has occurred: {e}')
        try:
            with zipfile.ZipFile(zipFilename, 'r') as myZip:
                myZip.extractall(gzipDir)
                gzipFolderName = os.listdir(gzipDir)[0]
                gzipSubDir = f'{gzipDir}/{gzipFolderName}'
                try:
                    for filename in os.listdir(gzipSubDir):
                        gzipFilename = f'{gzipSubDir}/{filename}'
                        saveFilename = f'{saveDir}/amplitude_data_{filename.split('.')[0]}.json'
                        try:
                            with gzip.open(gzipFilename, 'rt') as f:
                                file_content = f.read()
                                try:
                                    with open(saveFilename, 'w') as file:
                                        json.dump(file_content, file) # change so the filename is from the gzip
                                except Exception as e:
                                    print(f'{e}')
                        except Exception as e:
                            print(f'{e}')
                except Exception as e:
                    print(f'{e}')
        except Exception as e:
            print(f'{e}')

    else:
        print(f'The call was successful, but no data were retrieved.')
        logger.info('The call was successful, but no data were retrieved.')

# if statusCode == 200:
#     data = response.content
#     if len(data) > 0:
#         try:
#             with open(zipFilename, 'wb') as zipFile:
#                 zipFile.write(data)
#                 print('.zip file from response retrieved. Extracting...')
#                 logger.info(f'Master zip file {zipFilename} was successfully saved to local.')
#         except Exception as e:
#             print(f'Error saving master zip file: {e}')
#             logger.error(f'Error extracing master zip file: {e}')

#             try:
#                 with zipfile.ZipFile(zipFilename, 'r') as myZip:
#                     myZip.extractall(gzipDir)
#                     gzipFolderName = os.listdir(gzipDir)[0]
#                     gzipSubDir = f'{gzipDir}/{gzipFolderName}'
#                     for filename in os.listdir(gzipSubDir):
#                         gzipFilename = f'{gzipSubDir}/{filename}'
#                         saveFilename = f'{saveDir}/amplitude_data_{filename.split('.')[0]}.json'
#                         try:
#                             with gzip.open(gzipFilename, 'rt') as f:
#                                 file_content = f.read()
#                                 with open(saveFilename, 'w') as file:
#                                     json.dump(file_content, file) # change so the filename is from the gzip
#                         except Exception as e:
#                             print(f'Error extracting gzip files: {e}')
#             except Exception as e:
#                 print(f'Error opening saved zip file: {e}')



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


