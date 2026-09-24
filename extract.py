import requests
import os
from datetime import timedelta
from datetime import datetime
from dotenv import load_dotenv
import logging
import zipfile

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
saveDir = 'data'
os.makedirs(saveDir, exist_ok = True)

logDir = 'log'
os.makedirs(logDir, exist_ok = True)

timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
filename = f'{saveDir}/amplitude_datsa_{timestamp}.zip'
logFilename = f'{logDir}/amplitude_log_{timestamp}.json'

#get data
response = requests.get(url, params = params, auth = (api_key, secret_key))
statusCode = response.status_code

if statusCode == 200:
    print('Response successful.')

    data = response.content
    print(type(data))

    with open(filename, 'wb') as file:
        file.write(data)

        # with open(filename, 'w') as file:
        #     json.dump(data, file)
    # except Exception as e:
    #     print(f'Fatal error: {e}')
elif statusCode == 400:
    print('The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.')
elif statusCode == 404:
    print('No data available for the time range requested.')
elif statusCode == 504:
    print('The amount of data is large causing a timeout. For large amounts of data, use the Amazon S3 destination.')
else:
    print(f'Error: {statusCode}')


