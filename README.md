# Amplitude API

Extracts data from the Amplitude API using python.

## Description

The Amplitude API allows users to download a .zip file of website analytics data via Amplitude. On day's worth of data is extracted at a time. By default, the extracted date is yesterday relative to the system time.

The response is zip compressed file containing several .gz files. One .gz file corresponds to one hour of analytics data. Each .gz file is extracted into ROOT/data/ as a .json file.

Logs are generated each run and stored in ROOT/log/.

## Getting Started

This module relies on python. It is recommended to set up a python virtual environment and pip install the packages listed in Dependencies therein.

The API authentification is relies on .env file. Create a .env file defining two variables:
* AMP_API_KEY
* AMP_SECRET_KEY

You can obtain your Amplitude API key and secret key from your Amplitude account. Incorrect or missing authentification information will result a 403 authentification error.

### Dependencies

The following non-native packages need to be installed:
* python-dotenv
* boto3
* requests

See requirements.txt for the specific libraries and versions used.

This code was compiled using python version 3.12.10.

## Authors

Freya Marijatta

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
