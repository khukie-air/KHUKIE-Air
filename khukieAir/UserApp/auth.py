import jwt
import boto3
from django.conf import settings
from ..S3App.models import Folder
KHUKIEAIR_CONFIG = getattr(settings, "KHUKIEAIR_CONFIG", None)

class Cognito():
    region = KHUKIEAIR_CONFIG['aws']['cognito']['region']
    user_pool_id = KHUKIEAIR_CONFIG['aws']['cognito']['user_pool_id']
    app_client_id = KHUKIEAIR_CONFIG['aws']['cognito']['app_client_id']
    identity_pool_id = KHUKIEAIR_CONFIG['aws']['cognito']['identity_pool_id']
    account_id = KHUKIEAIR_CONFIG['aws']['common']['account_id']
    aws_access_key_id = KHUKIEAIR_CONFIG['aws']['common']['aws_access_key_id']
    aws_secret_access_key = KHUKIEAIR_CONFIG['aws']['common']['aws_secret_access_key']

    def sign_up(self, username, password, UserAttributes):
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        response = client.sign_up(ClientId=self.app_client_id,
                                  Username=username,
                                  Password=password,
                                  UserAttributes=UserAttributes)

        client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
        )

        return response

    def confirm_sign_up(self, username):
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        response = client.admin_confirm_sign_up(UserPoolId=self.user_pool_id, Username=username)
        return response

    def sign_in_admin(self, username, password):
        # Get ID Token
        idp_client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        response = idp_client.admin_initiate_auth(UserPoolId=self.user_pool_id,
                                              ClientId=self.app_client_id,
                                              AuthFlow='ADMIN_NO_SRP_AUTH',
                                              AuthParameters={'USERNAME': username,'PASSWORD': password})

        provider = 'cognito-idp.%s.amazonaws.com/%s' % (self.region, self.user_pool_id)
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Get IdentityId
        ci_client = boto3.client('cognito-identity', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        response = ci_client.get_id(AccountId=self.account_id,
                                IdentityPoolId=self.identity_pool_id,
                                Logins={provider: id_token})

        # Get Credentials
        response = ci_client.get_credentials_for_identity(IdentityId=response['IdentityId'], Logins={provider: id_token})

        # Get User info
        user_claims = jwt.decode(id_token, verify=False)

        # Create root folder object
        Folder.objects.create(path=response['IdentityId']+'/root/', parent_folder_id=None, folder_name='root')

        # User Token
        result = {
            'User': {
                'id': user_claims['cognito:username'],
                'sub': user_claims['sub'],
                'name': user_claims['name'],
                'email': user_claims['email']
            },
            'IdentityId': response['IdentityId'],
            'IdToken': id_token,
            'AccessToken': access_token,
            'RefreshToken': refresh_token,
            'Credentials': {
                'AccessKeyId': response['Credentials']['AccessKeyId'],
                'SessionToken': response['Credentials']['SessionToken'],
                'SecretKey': response['Credentials']['SecretKey']
            }
        }

        return result

    def sign_out(self, access_token):
        # Get Client
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        try:
            client.global_sign_out(
                AccessToken=access_token
            )
        except client.exceptions.NotAuthorizedException:
            return {'message': '로그인 상태에 문제가 있습니다. 다시 시도해주세요. (NotAuthorizedException)'}
        except Exception as exc:
            return {'message': '로그아웃 처리에 실패했습니다. ' + str(exc)}

        return None

    def delete_user(self, access_token):
        # Get Client
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        try:
            client.delete_user(
                AccessToken=access_token
            )
        except client.exceptions.NotAuthorizedException:
            return {'message': '로그인 상태에 문제가 있습니다. 다시 시도해주세요. (NotAuthorizedException)'}
        except Exception as exc:
            return {'message': '탈퇴 처리에 실패했습니다. ' + str(exc)}

        return None

    def change_password(self, access_token, prevpw, newpw):
        # Get Client
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        try:
            client.change_password(
                PreviousPassword=prevpw,
                ProposedPassword=newpw,
                AccessToken=access_token
            )
        except client.exceptions.NotAuthorizedException:
            return {'message': '로그인 상태에 문제가 있습니다. 다시 시도해주세요. (NotAuthorizedException)'}
        except Exception as exc:
            return {'message': '비밀번호 변경에 실패했습니다. ' + str(exc)}

        return None

    def forgot_password(self, username):
        # Get Client
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)

        resp = client.forgot_password(
            ClientId=self.app_client_id,
            Username=username
        )

        return resp

    def confirm_forgot_password(self, username, password, code):
        # Get Client
        client = boto3.client('cognito-idp', self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)
        
        try:
            client.confirm_forgot_password(
                ClientId=self.app_client_id,
                Username=username,
                ConfirmationCode=code,
                Password=password
            )
        except client.exceptions.LimitExceededException:
            return {'message': '변경 요청 횟수를 초과했습니다. 1분 뒤 다시 요청해주세요.'}
        except Exception as exc:
            return {'message': '비밀번호 변경 처리에 실패했습니다. ' + str(exc)}

        return None