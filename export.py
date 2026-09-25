import io
import os
import uuid
import boto3
from boto3.s3.transfer import S3UploadFailedError
from dotenv import load_dotenv
# from botocore.exceptions import ClientError

load_dotenv(override = True)

access_key = os.getenv('DENG_AWS_ACCESS_KEY')
secret_key = os.getenv('DENG_AWS_SECRET_KEY')
bucket_name = os.getenv('DENG_BUCKET_NAME')


s3 = boto3.client('s3',
                  aws_access_key_id = access_key,
                  aws_secret_access_key = secret_key
                  )

#List all buckets
response =  s3.list_buckets()
for bucket in response['Buckets']:
    print(f'Bucket: {bucket['Name']}')

#Need to set up a policy in aws before continuing
# bucket_name = f"amzn-s3-demo-bucket-{uuid.uuid4()}"
#     bucket = s3_resource.Bucket(bucket_name)

# response = boto3.client.list_buckets(
#     MaxBuckets=123,
#     ContinuationToken='string',
#     Prefix='string',
#     BucketRegion='string'
# )