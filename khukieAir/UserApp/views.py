import jwt
import json
import hashlib
from django.contrib.auth import authenticate, login

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .auth import Cognito
from .models import User

class Login(APIView):
    def post(self, request):
        # 파라미터가 전부 입력되었는지 확인
        required_keys = ['id', 'pw']
        if all(it in request.POST for it in required_keys):
            if User.objects.filter(username=request.POST['id']).count() == 0:
                return Response({'message': '존재하지 않는 아이디입니다.'}, status=400)

            username = request.POST['id']
            password = request.POST['pw']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                hashcode = hashlib.md5(request.POST['pw'].encode('utf-8')).hexdigest()
                cog = Cognito()
                result = cog.sign_in_admin(username=username, password=hashcode)
                return Response(result, status=200)
            else:
                return Response({'message': '아이디 혹은 비밀번호가 잘못되었습니다.'}, status=401)

        else:
            return Response({'message': '요구되는 파라미터를 전부 입력해주세요.'}, status=400)

class Signup(APIView):
    def post(self, request):        
        # 파라미터가 전부 입력되었는지 확인
        required_keys = ['id', 'pw', 'email', 'name']
        if all(it in request.POST for it in required_keys):
            if User.objects.filter(username=request.POST['id']).count():
                return Response({'message': '이미 존재하는 아이디입니다.'}, status=400)
            if User.objects.filter(email=request.POST['email']).count():
                return Response({'message': '이미 존재하는 이메일입니다.'}, status=400)

            hashcode = hashlib.md5(request.POST['pw'].encode('utf-8')).hexdigest()
            user = User.objects.create_user(
                username=request.POST['id'],
                email=request.POST['email'],
                password=request.POST['pw'],
                name=request.POST['name']
            )

            cog = Cognito()
            cog.sign_up(
                username=request.POST['id'],
                password=hashcode,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': request.POST['email']
                    },
                    {
                        'Name': 'name',
                        'Value': request.POST['name']
                    }
                ]
            )
            cog.confirm_sign_up(username=request.POST['id'])
            return Response({'message': '회원가입이 성공하였습니다.'}, status=200)

        # 파라미터가 누락된 경우
        else:
            return Response({'message': '요구되는 파라미터를 전부 입력해주세요.'}, status=400)

class Logout(APIView):
    def post(self, request):
        if 'Authorization' not in request.headers:
            return Response({'message': 'Access Token을 전달해주세요.'}, status=401)
        access_token = request.headers['Authorization'].replace('Bearer ', '')

        cog = Cognito()

        resp = cog.sign_out(access_token)
        if resp is not None:
            return Response(resp, status=400)
            
        return Response({'message': '로그아웃에 성공했습니다.'}, status=200)

class Dropout(APIView):
    def delete(self, request):
        if 'Authorization' not in request.headers:
            return Response({'message': 'Access Token을 전달해주세요.'}, status=401)
        access_token = request.headers['Authorization'].replace('Bearer ', '')

        claims = jwt.decode(access_token, verify=False)
        user = User.objects.filter(username=claims['username'])
        if user.count() == 0:
            return Response({'message': '이미 탈퇴 처리된 계정입니다.'}, status=400)
        user.delete()

        cog = Cognito()
        resp = cog.delete_user(access_token)

        if resp is not None:
            return Response(resp, status=400)
            
        return Response({'message': '탈퇴 처리에 성공했습니다.'}, status=200)

class Duplicate(APIView):
    def get(self, request, id):
        if id is None:
            return Response({'message': '조회할 ID를 Path Parameter로 보내주세요.'}, status=404)
        
        if User.objects.filter(username=str(id)).count() != 0:
            return Response({'message': '이미 존재하는 ID입니다.'}, status=500)
        
        return Response({'id': id, 'is_duplicate': False}, status=200)

class Info(APIView):
    def post(self, request):
        if 'Authorization' not in request.headers:
            return Response({'message': 'Access Token을 전달해주세요.'}, status=401)
        access_token = request.headers['Authorization'].replace('Bearer ', '')

        required_keys = ['old_pw', 'new_pw']
        if all(it in request.POST for it in required_keys):
            
            claims = jwt.decode(access_token, verify=False)
            user = User.objects.filter(username=claims['username'])[0]
            user.set_password(request.POST['new_pw'])

            hashed_old_pw = hashlib.md5(request.POST['old_pw'].encode('utf-8')).hexdigest()
            hashed_new_pw = hashlib.md5(request.POST['new_pw'].encode('utf-8')).hexdigest()

            cog = Cognito()
            resp = cog.change_password(access_token, hashed_old_pw, hashed_new_pw)

            if resp is not None:
                return Response(resp, status=400)
                
            return Response({'message': '비밀번호 변경에 성공했습니다.'}, status=200)
        
        else:
            return Response({'message': 'old_pw와 new_pw를 전달해주세요.'}, status=400)

class Findpw(APIView):
    def post(self, request):

        required_keys = ['id']
        if all(it in request.POST for it in required_keys):
            cog = Cognito()
            resp = cog.forgot_password(username=request.POST['id'])

            return Response(resp, status=200)

        else:
            return Response({'message': 'id를 전달해주세요.'}, status=400)

class Resetpw(APIView):
    def post(self, request):

        required_keys = ['id', 'pw', 'confirmation_code']
        if all(it in request.POST for it in required_keys):
            hashcode = hashlib.md5(request.POST['pw'].encode('utf-8')).hexdigest()

            user = User.objects.get(username=request.POST['id'])
            user.password = request.POST['pw']
            user.save()

            cog = Cognito()
            resp = cog.confirm_forgot_password(
                username=request.POST['id'],
                password=hashcode,
                code=request.POST['confirmation_code']
            )

            if resp is not None:
                return Response(resp, status=400)

            return Response({'message': '비밀번호 변경에 성공했습니다.'}, status=200)

        else:
            return Response({'message': 'id, pw, confirmation_code를 모두 전달해주세요.'}, status=400)