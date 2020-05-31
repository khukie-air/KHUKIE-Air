"""
Precondition : AWS Configuration was setted in project settings.
예정 :
-auto folder create 래퍼런스찾기
-ACL처리 역시 틀 갖춘 후 공부하고 처리할 것.
-예외처리는 슈도와 틀 모두 갖춘 후. views.py와 구조 따져할 것.
-시간남으면 주석달 것.
"""
import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

# temp aws config setting
# https://mingrammer.com/ways-to-manage-the-configuration-in-python/
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
AWS_ACCESS_KEY_ID = config['default']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['default']['AWS_SECRET_ACCESS_KEY']
AWS_BUCKET_NAME = config['s3']['AWS_BUCKET_NAME']
#AWS_DEFAULT_REGION = config['defualt']['AWS_DEFAULT_REGION'] #s3는 region설정이 필요없다.
# --------------------------------


# boto3 s3 code example : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = s3.Bucket(AWS_BUCKET_NAME)
FILE_PRESIGNED_URL_EXPIRATION = 3600


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

def get_file(file_key):
    print(AWS_BUCKET_NAME)
    print(file_key)
    file = s3.Object(AWS_BUCKET_NAME, file_key).get()
    return file

def get_file_info(file_key, fields):
    """
    db에서 불러와야하나?
    :param file_key:
    :param fields:
    :return:
    """
    file = get_file(file_key)
    return file


def copy_file(source_key, destination_key):
    """
    현재는 카피만 callback 추가될 수도 있어보여
    """
    copy_source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': source_key
    }
    s3.Object(AWS_BUCKET_NAME, destination_key).copy_from(CopySource=copy_source)
    #copy 결과에 따른 return
    return True

def remove_file(file_key):
    """
    db상에 지운표시하거나 방법 정해지면할 것
    """
    s3.Object(AWS_BUCKET_NAME, file_key)
    
    return True

def rename_or_move_file(old_key, new_key):
    source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': old_key
    }
    s3.Object(AWS_BUCKET_NAME, new_key).copy_from(CopySource=source)
    s3.Object(AWS_BUCKET_NAME, old_key).delete()
    return True
