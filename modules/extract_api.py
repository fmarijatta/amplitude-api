import os
import requests
import logging
import zipfile
import gzip
import shutil
import boto3
from datetime import timedelta
from datetime import datetime
import time


def extract_json(chosenDate:str, url:str, amp_api_key:str, amp_secret_key:str, aws_access_key:str, aws_secret_key:str, aws_bucket_name:str, saveDir:str, nAttempts = 15, delay = 10):
    """_summary_

    Args:
        chosenDate (str): which date to extract. 'yesterday' will call the previous day relative to the system date. Otherwise input a string with the format %Y%m%d, e.g. 20240131 for 1st Jan 2024.
        url (str): The url to call from the API.
        amp_api_key (str): Amplitude API access key.
        amp_secret_key (str): Amplitude secret access key.
        aws_access_key (str): AWS access key.
        aws_secret_key (str): AWS secret access key.
        aws_bucket_name (str): The name of the S3 bucket to upload the data to.
        saveDir (str): File directory to save extracted json files.
        nAttempts (int, optional): How many times the API call can be reattempted. Defaults to 15.
        delay (int, optional): Delay in seconds before reattempting API call. Defaults to 10.
    """

    logger = logging.getLogger(__name__)
    
    #Choose the date to extract. Either 'yesterday' or input a specific date as a string
    if chosenDate == 'yesterday':
        daterange = (datetime.today() - timedelta(days = 1)).strftime('%Y%m%d')
    else:
        try:
            datetime.strptime(chosenDate, '%Y%m%d')
            daterange = chosenDate
        except:
            print("The variable chosenDate must be either 'yesterday' or a specific date structured as YYYYMMDD. Please change the variable and try again.")

    params = {
        'start': f'{daterange}T00',
        'end': f'{daterange}T23'
        }
    
    #Create temporary directories for zip and gzip files
    zipDir = f'zip/{daterange}'
    os.makedirs(zipDir, exist_ok = True)
    gzipDir = f'{zipDir}/gzip/'
    os.makedirs(gzipDir, exist_ok = True)
    zipFilename = f'{zipDir}/amplitude_data_{daterange}.zip'

    ###Compare planned extraction to existing files in S3 bucket

    #Obtain a list of files for this daterange in the s3 bucket
    s3Filename = datetime.strptime(daterange, '%Y%m%d').strftime('%Y-%m-%d')

    try:
        session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        s3 = session.resource('s3')
        my_bucket = s3.Bucket(aws_bucket_name)
        s3_files = []
        for obj in my_bucket.objects.all():
            s3file = obj.key
            if s3file.find(s3Filename) != -1:
                s3_files.append(int(s3file.split('.')[0].split('_')[-1]))

        #Check whether any of the daterange's data is already in the s3 bucket. We'd expect 24 files for one day, so numbered
        if sorted(s3_files) == list(range(0,24)): 
            print(f'Data for {daterange} is already in the s3 bucket. Data extraction aborted.')
            logger.info('Data for this date is already in the s3 bucket. Data extraction aborted.')
            continueFlag = 0
        elif s3_files != []:
            print(f'Warning: only partial data for {daterange} exists in s3 bucket. Reattempting API call.')
            logger.warning(f'Warning: only partial data for {daterange} exists in s3 bucket. Data extraction will be attempted.')
            continueFlag = 1
        else:
            continueFlag = 1
    except Exception as e:
        print(f'Warning: could not read data already in s3 bucket. Data extraction will be attempted regardless. Error: {e}')
        logger.error(f'Error while parsing s3 bucket: {e}')
        continueFlag = 1

    ### API call

    #If daterange's data is either not in or incompletely in s3 (or if this could not verified either way), then attempt API call
    if continueFlag == 1:
        # Perform call
        for i in range (nAttempts):
            response = requests.get(url, params = params, auth = (amp_api_key, amp_secret_key))
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
                time.sleep(delay)
            else:
                print(f'Error: {statusCode}')
                logger.error(f'Unknown error: {statusCode}')
                break # For unknown 300+ errors, break instead of retrying

    # Remove the zip directory
    shutil.rmtree('zip')