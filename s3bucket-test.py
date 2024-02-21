
import boto3

from config import DevelopmentConfig as devconf

BUCKET_NAME = "country-flag-image-bucket"
aws_region = 'eu-west-2'
s3 = boto3.client('s3', region_name=aws_region, aws_access_key_id=f"{devconf.AWS_ACCESS_KEY_ID}", aws_secret_access_key=f"{devconf.SECRET_KEY}")

buckets_response = s3.list_buckets()

#for bucket in buckets_response["Buckets"]:
            #print(bucket)
images = list()

response = s3.list_objects_v2(Bucket=BUCKET_NAME)
counter = 0
for obj in response["Contents"]: 
    print(counter)
    if counter > 0:
        url = s3.generate_presigned_url(
        "get_object", 
        Params={"Bucket":BUCKET_NAME,  "Key": obj['Key']}, 
        ExpiresIn=30)
        images.append(url)
    counter +=1

print(response)
