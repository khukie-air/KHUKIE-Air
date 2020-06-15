import jwt

def get_user_info(access_token):
    claims = jwt.parse(access_token, verify=False)
    return claims