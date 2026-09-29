# Amplitude API

Extracts data from the Amplitude API using python and uploads to s3.

## Description

The Amplitude API allows users to download a .zip file of website analytics data via Amplitude. extract.py extracts one day's worth of data at a time. By default, the extracted date is yesterday relative to the system time.

The response is zip compressed file containing several .gz files. One .gz file corresponds to one hour of analytics data. Each .gz file is extracted into ROOT/data/ as a .json file. The extracted zip files are only temporarily stored locally but will be deleted after the script has run. Once stored locally, load.py can upload all data to a designated s3 bucket.

Extract and load logs are generated each run and stored in ROOT/log/.

## Getting Started

### Python
This module relies on python. It is recommended to set up a python virtual environment and pip install the following packages:
* python-dotenv
* boto3
* requests

The API authentification relies on .env file. Create a .env file defining five variables:
* AMP_API_KEY
* AMP_SECRET_KEY
* AWS_ACCESS_KEY
* AWS_SECRET_KEY
* AWS_BUCKET_NAME

### Amplitude
You can obtain your Amplitude API key and secret key from your Amplitude account. Incorrect or missing authentification information will result a 403 authentification error.

### S3
Access to the s3 bucket is dependent on settings within AWS. As stated above, you will need to provide the bucket name alongside an access key and secret. The policy attached to the user should allow the following permissions for S3:
* ListBucket
* GetObject
* PutObject
 
And the following permissions for KMS:
* DescribeKey
* Encrypt
* GenerateDataKey
* Decrypt

### Other dependencies

See [requirements.txt](https://github.com/fmarijatta/amplitude-api/blob/main/requirements.txt) for the specific libraries and versions used.

This code was compiled using python version 3.12.10.

## Authors

Freya Marijatta

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.