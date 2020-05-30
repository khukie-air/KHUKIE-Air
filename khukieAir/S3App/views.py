from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class FileDetail(APIView):
    """
    Retrieve, update or delete a file.
    """
    def get(self, request, pk, format=None):
        print("파일정보조회")
        return Response(status=200)

    def post(self,request,pk,format=None):
        print("파일복사")
        return Response(status=200)

    def delete(self,request,pk,format=None):
        print("파일삭제")
        return Response(status=200)

class FileUpload(APIView):
    """
    Create a file from client to s3 bucket
    """
    def post(self,request,format=None):
        print("파일업로드")
        return Response(status=200)

class FileRename(APIView):
    def put(self,request,pk,format=None):
        print("파일 이름변경")
        return Response(status=200)

class FileMove(APIView):
    def put(self,request,pk,format=None):
        print("파일 이동")
        return Response(status=200)

class FolderCreation(APIView):
    def post(self,request,format=None):
        print("폴더 생성")
        return Response(status=200)

class FolderDetail(APIView):
    def get(self,request,pk,format=None):
        print("폴더정보 조회")
        return Response(status=200)
    def post(self,request,pk,format=None):
        print("폴더 복사")
        return Response(status=200)
    def delete(self,request,pk,format=None):
        print("폴더 삭제")
        return Response(status=200)

class FolderItemList(APIView):
    def get(self,request,pk,format=None):
        print("폴더 내 아이템 파일과 폴더 목록 조회")
        return Response(status=200)

class FolderRename(APIView):
    def put(self,request,pk,format=None):
        print("폴더 이름변경")
        return Response(status=200)

class FolderMove(APIView):
    def put(self,request,pk,format=None):
        print("폴더 이동")
        return Response(status=200)

class TrashList(APIView):
    def get(self,request,format=None):
        print("버린 아이템 목록 조회")
        return Response(status=200)

class TrashControl(APIView):
    def post(self,request,pk,format=None):
        print("버린 아이템 복구")
        return Response(status=200)

    def delete(self,request,pk,format=None):
        print("버린 아이템 완전 삭제")
        return Response(status=200)