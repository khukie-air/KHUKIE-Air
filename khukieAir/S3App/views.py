from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from . import s3_bucket_sdk
# Create your views here.
def is_owner(request):
    """
    예정 : request로부터 해당 bucket내 user folder 접근권한 체크
    :return: boolean
    """
    return True

def get_file_key(request):
    """
    bucket내 object의 절대경로를 key라고 부름.
    pk의 정의와 정보넘김 필요성 정리 필요한 듯 ㅎ다ㅏ.
    :param request:
    :return:
    """
    file_key = '1/temp/temp/s3test.txt'
    return file_key

class FileRetrieveCopyDelete(APIView):
    """
    Retrieve, update or delete a file.
    """
    def get(self, request, pk, format=None):
        if is_owner(request):
            file_key = get_file_key(request)
            fields = request.data['fields'].split(',') if 'fields' in request.data else None
            file_info = s3_bucket_sdk.get_file_info(file_key, fields)
            print(file_info)
            return Response(status=200)
        else:
            raise PermissionDenied

    def post(self,request,pk,format=None):
        if is_owner(request):
            #request로 부터 destination과 source추출
            source_key = '1/temp/s3test.txt'
            destination_key = '1/temp/tmp/s3test2.txt'
            response = s3_bucket_sdk.copy_file(source_key, destination_key)
            return Response(status=200)
        else:
            raise PermissionDenied


    def delete(self,request,pk,format=None):
        if is_owner(request):
            file_key = '1/temp/temp/s3test.txt'
            response = s3_bucket_sdk.remove_file(file_key)
            return Response(status=200)
        else:
            raise PermissionDenied

class FileUploadLinkCreate(APIView):
    """
    Create a file from client to s3 bucket
    """
    def post(self,request,format=None):
        if is_owner(request):
            #1 file_key얻어내기(임시)
            file_key = get_file_key(request)
            if file_key is None:
                print("에러발생시킬 것")

            #2 fields, conditions, expiretime 생성

            #3호출로 링크따오기
            response = s3_bucket_sdk.create_presigned_post(file_key)
            return Response(response)
        else:
            raise PermissionDenied

class FileRename(APIView):
    def put(self,request,pk,format=None):
        if is_owner(request):
            #request로 부터 새이름과 대상 추출
            old_key = '1/s3test.txt'
            new_key = '1/s3test2.txt'
            response = s3_bucket_sdk.rename_or_move_file(old_key=old_key, new_key=new_key)
            return Response(status=200)
        else:
            raise PermissionDenied


class FileMove(APIView):
    def put(self,request,pk,format=None):
        if is_owner(request):
            # request로 부터 새이름과 대상 추출
            old_key = '1/s3test2.txt'
            new_key = '1/test2/s3test2.txt'
            response = s3_bucket_sdk.rename_or_move_file(old_key=old_key, new_key=new_key)
            return Response(status=200)
        else:
            raise PermissionDenied

class FolderCreate(APIView):
    def post(self,request,format=None):
        if is_owner(request):
            response = s3_bucket_sdk.create_folder('1/1/1/')
            return Response(response)
        else:
            raise PermissionDenied


class FolderRetrieveCopyDelete(APIView):
    def get(self,request,pk,format=None):
        if is_owner(request):

            response = s3_bucket_sdk.get_folder_info('1/')
            return Response(response)
        else:
            raise PermissionDenied


    def post(self,request,pk,format=None):
        if is_owner(request):
            old_key = '1/1/1/'
            destination_prefix = '1/1/1/2/'
            folder_name = '1'
            response = s3_bucket_sdk.copy_folder(old_key,destination_prefix, folder_name)
            return Response(response)
        else:
            raise PermissionDenied


    def delete(self,request,pk,format=None):
        if is_owner(request):
            response = s3_bucket_sdk.remove_folder('1/test2/')
            return Response(response)
        else:
            raise PermissionDenied


class FolderItemList(APIView):
    def get(self,request,pk,format=None):
        if is_owner(request):
            response = s3_bucket_sdk.get_items_in_folder("1/")
            return Response(response)
        else:
            raise PermissionDenied


class FolderRename(APIView):
    def put(self,request,pk,format=None):
        if is_owner(request):
            response = s3_bucket_sdk.rename_folder(old_key="1/1/1/", old_folder_name="1", new_key= "4")
            return Response(response)
        else:
            raise PermissionDenied

class FolderMove(APIView):
    def put(self,request,pk,format=None):
        if is_owner(request):
            response = s3_bucket_sdk.rename_folder(old_key="1/1/4/2/1", old_folder_name="1", new_key= "1/1/3/2")
            return Response(response)
        else:
            raise PermissionDenied

class TrashList(APIView):
    def get(self,request,format=None):
        if is_owner(request):
            print("버린 아이템 목록 조회")
            return Response(status=200)
        else:
            raise PermissionDenied

class TrashControl(APIView):
    def post(self,request,pk,format=None):
        if is_owner(request):
            print("버린 아이템 복구")
            return Response(status=200)
        else:
            raise PermissionDenied

    def delete(self,request,pk,format=None):
        if is_owner(request):
            print("버린 아이템 완전 삭제")
            return Response(status=200)
        else:
            raise PermissionDenied
