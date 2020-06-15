"""
Precondition : AWS Configuration was setted in project settings.
예정 :
-중간경로 object역시 직접 생성해야하더라!!!!!
-auto folder create 래퍼런스찾기
-ACL처리 역시 틀 갖춘 후 공부하고 처리할 것.
-예외처리는 슈도와 틀 모두 갖춘 후. views.py와 구조 따져할 것.
- folder file명에 슬래시 포함불가
-시간남으면 주석달 것.
"""
import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

# temp aws config setting
# https://mingrammer.com/ways-to-manage-the-configuration-in-python/
from django.conf import settings

KHUKIEAIR_CONFIG = getattr(settings, "KHUKIEAIR_CONFIG", None)

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_BUCKET_NAME = KHUKIEAIR_CONFIG['aws']['s3']['bucket_name']
#AWS_DEFAULT_REGION = config['defualt']['AWS_DEFAULT_REGION'] #s3는 region설정이 필요없다.
# --------------------------------


# boto3 s3 code example : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = s3.Bucket(AWS_BUCKET_NAME)
FILE_PRESIGNED_URL_EXPIRATION = 3600

def test():
    return s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)

def create_presigned_post(file_name, fields=None, conditions=None, expiration=FILE_PRESIGNED_URL_EXPIRATION):
    """
    Generate a presigned URL S3 POST request to upload a file
    :param file_name: string (absolute path in the bucket)
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    try:
        response = s3_client.generate_presigned_post(AWS_BUCKET_NAME, file_name, Fields=fields, Conditions=conditions,
                                              ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response

def get_object(key):
    obj = s3.Object(AWS_BUCKET_NAME, key)
    return obj



def copy_file(source_key, destination_key):
    """
    현재는 카피만 callback 추가될 수도 있어보여
    """
    copy_source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': source_key
    }
    get_object(destination_key).copy_from(CopySource=copy_source)

def remove_file(file_key):
    """
    db상에 지운표시하거나 방법 정해지면할 것
    """
    get_object(file_key)
    
    return True

def rename_or_move_file(old_key, new_key):
    source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': old_key
    }
    get_object(new_key).copy_from(CopySource=source)
    get_object(old_key).delete()
#get_file refactor






def create_folder(folder_key):
    response = s3_client.put_object(Bucket=AWS_BUCKET_NAME, Key=folder_key)

def rename_or_move_folder(old_key, old_folder_name,new_key):
    old_prefix = old_key[:old_key.rfind(old_folder_name)]
    for item in bucket.objects.filter(Prefix=old_key):
        old_source = {'Bucket': AWS_BUCKET_NAME, 'Key': item.key}
        new_item_key = item.key.replace(old_key, new_key, 1)
        get_object(new_item_key).copy_from(CopySource=old_source)
        item.delete()


def copy_folder(old_key, destination_prefix, folder_name):
    old_prefix = old_key[:old_key.rfind(folder_name)]
    for item in bucket.objects.filter(Prefix=old_key):
        print(item)
        old_source = {'Bucket': AWS_BUCKET_NAME,'Key': item.key}
        new_item_key = item.key.replace(old_prefix, destination_prefix, 1)
        get_object(new_item_key).copy_from(CopySource=old_source)


def remove_folder(folder_key):
    for item in bucket.objects.filter(Prefix=folder_key):
        item.delete()
    return True
