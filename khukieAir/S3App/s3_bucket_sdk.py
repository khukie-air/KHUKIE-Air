import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.exceptions import PermissionDenied
KHUKIEAIR_CONFIG = getattr(settings, "KHUKIEAIR_CONFIG", None)

COMMON_AWS_ACCESS_KEY_ID = KHUKIEAIR_CONFIG['aws']['common']['aws_access_key_id']
COMMON_AWS_SECRET_ACCESS_KEY = KHUKIEAIR_CONFIG['aws']['common']['aws_secret_access_key']
AWS_BUCKET_NAME = KHUKIEAIR_CONFIG['aws']['s3']['bucket_name']


def get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN):
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=AWS_SESSION_TOKEN)
    return s3, s3_client

# boto3 s3 code example : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html

FILE_PRESIGNED_URL_EXPIRATION = 3600



def create_presigned_url(s3_client, object_name, expiration=FILE_PRESIGNED_URL_EXPIRATION):
    """Generate a presigned URL to share an S3 object

    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': AWS_BUCKET_NAME,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def create_presigned_post(s3_client, file_name, fields=None, conditions=None, expiration=FILE_PRESIGNED_URL_EXPIRATION):
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

def get_object(s3, key):
    obj = s3.Object(AWS_BUCKET_NAME, key)
    return obj



def copy_file(s3, source_key, destination_key):
    """
    현재는 카피만 callback 추가될 수도 있어보여
    """
    copy_source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': source_key
    }
    get_object(s3, destination_key).copy_from(CopySource=copy_source)

def remove_file(s3, file_key):
    get_object(s3, file_key).delete()


def rename_or_move_file(s3, old_key, new_key):
    source = {
        'Bucket': AWS_BUCKET_NAME,
        'Key': old_key
    }
    get_object(s3, new_key).copy_from(CopySource=source)
    get_object(s3, old_key).delete()
#get_file refactor






def create_folder(s3_client, folder_key):
    response = s3_client.put_object(Bucket=AWS_BUCKET_NAME, Key=folder_key)

def rename_or_move_folder(s3, old_key, old_folder_name,new_key):
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    old_prefix = old_key[:old_key.rfind(old_folder_name)]
    for item in bucket.objects.filter(Prefix=old_key):
        old_source = {'Bucket': AWS_BUCKET_NAME, 'Key': item.key}
        new_item_key = item.key.replace(old_key, new_key, 1)
        get_object(s3, new_item_key).copy_from(CopySource=old_source)
        item.delete()


def copy_folder(s3, old_key, destination_prefix, folder_name):
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    old_prefix = old_key[:old_key.rfind(folder_name)]
    for item in bucket.objects.filter(Prefix=old_key):
        old_source = {'Bucket': AWS_BUCKET_NAME,'Key': item.key}
        new_item_key = item.key.replace(old_prefix, destination_prefix, 1)
        get_object(s3, new_item_key).copy_from(CopySource=old_source)


def remove_folder(s3, folder_key):
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    for item in bucket.objects.filter(Prefix=folder_key):
        item.delete()
    return True
