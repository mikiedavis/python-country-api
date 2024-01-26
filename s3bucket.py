
import boto3

BUCKET_NAME = "country-flag-image-bucket"

s3 = boto3.client('s3', aws_access_key_id='AKIA5QL5DXKIJE2GHW5F', aws_secret_access_key='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')
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

#print(url)
