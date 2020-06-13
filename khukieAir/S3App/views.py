from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .models import File, Folder, Trash
from . import s3_bucket_sdk
from .serializers import FileSerializer, FolderSerializer
from copy import deepcopy
import datetime
import json
from collections import OrderedDict

# Create your views here.
def is_owner(request):
    """
    예정 : request로부터 해당 bucket내 user folder 접근권한 체크
    :return: boolean
    """
    return True


def get_file(pk):
    try:
        file = File.objects.get(file_id=pk)
        return file
    except ObjectDoesNotExist:
        return None


def get_folder(pk):
    try:
        folder = Folder.objects.get(folder_id=pk)
        return folder
    except ObjectDoesNotExist:
        return None
def get_object_name(obj_key):
    """
    [테스트용]
    """
    if obj_key.endswith('/'):
        start_idx = obj_key.rfind('/',0,len(obj_key)-1)
        start_idx+=1
        return obj_key[start_idx:len(obj_key)-1]
    else:
        start_idx = obj_key.rfind('/', 0,len(obj_key))
        start_idx+=1
        return obj_key[start_idx:len(obj_key)]
def get_object_size():
    """
    임시
    """
    return 5
class Synchronizer(APIView):

    def post(self, request, format=None):
        """
        [테스트용] s3 object로 db 초기화
        """
        File.objects.all().delete()
        Folder.objects.all().delete()
        response = s3_bucket_sdk.test()
        for obj in response['Contents']:
            if obj['Key'].endswith('/'):
                Folder.objects.create(path=obj['Key'],parent_folder_id=None,size=get_object_size(),folder_name=get_object_name(obj['Key']))
            else:
                File.objects.create(content_created_at=datetime.datetime.now(),content_modified_at=datetime.datetime.now(),path=obj['Key'],parent_folder_id=None,size=get_object_size(),file_name=get_object_name(obj['Key']))

        folders=Folder.objects.all()
        for folder in folders:
            if folder.path.count('/') > 1:
                parent_folder = Folder.objects.get(path=folder.path[:folder.path.rfind(folder.folder_name)])
                folder.parent_folder_id =parent_folder
                folder.save()
        files = File.objects.all()
        for file in files:
            if file.path.count('/') > 0:
                parent_folder = Folder.objects.get(path=file.path[:file.path.rfind(file.file_name)])
                file.parent_folder_id = parent_folder
                file.save()
        return Response(status=200)
class FileRetrieveCopyDelete(APIView):
    def get(self, request, pk, format=None):
        """
        파일 정보 조회
        """
        if is_owner(request):
            file = get_file(pk)
            if file is not None:
                fields = request.data['fields'].split(',') if 'fields' in request.data else None
                file_info_data = FileSerializer(file, fields=fields).data
                return Response(file_info_data, status=200)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise PermissionDenied

    def post(self,request,pk,format=None):
        """
        파일복사
        """
        if is_owner(request):
            #request로 부터 destination과 source추출
            source_file = get_file(pk)
            if source_file is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dest_folder_id = request.data['to_folder_id'] if 'to_folder_id' in request.data else None
            if dest_folder_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            dest_folder = get_folder(dest_folder_id)
            if dest_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            new_file=deepcopy(source_file)
            new_file.file_id = None
            new_file.created_at = new_file.modified_at = datetime.datetime.now()
            source_key = source_file.path
            if source_file.parent_folder_id.folder_id == dest_folder_id:
                #256글자는 어떻게?
                new_file.path+='-복사본'
                new_file.file_name +='-복사본'
                dest_key = new_file.path
            else:
                dest_key = dest_folder.path+source_file.file_name
                new_file.path = dest_key
                new_file.parent_folder_id = dest_folder
                if File.objects.filter(path=dest_key).exists(): #만약 dest_폴더에 겹치는게 있다면 db에서 지울것
                    File.objects.get(path=dest_key).delete()
            new_file.save()
            data = FileSerializer(new_file).data
            s3_bucket_sdk.copy_file(source_key, dest_key)
            return Response(data, status=200)
        else:
            raise PermissionDenied


    def delete(self,request,pk,format=None):
        """
        파일 삭제 (휴지통으로)
        """
        if is_owner(request):
            file = get_file(pk)
            if file is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            #Trash model 추가할것!!!!!!!!
            file.is_trashed = True
            file.save()
            return Response(status=200)
        else:
            raise PermissionDenied

class FileUploadLinkCreate(APIView):
    """
    Create a file from client to s3 bucket
    """
    #요청 접수해서 presigned url 주고 업로드완료 사인 받으면 db등록 후 file_info넘겨줄 것.
    def post(self,request,format=None):
        if is_owner(request):
            #1 file_key얻어내기(임시)
            file_key = request.data['path'] if 'path' in request.data else None
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
        """
        파일 이름 변경
        """
        if is_owner(request):
            #request로 부터 새이름과 대상 추출
            file = get_file(pk)
            if file is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            new_name = request.data['new_name'] if 'new_name' in request.data else None
            if new_name is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            old_key = file.path
            new_key = file.path = file.path[:file.path.rfind(file.file_name)]+new_name
            file.file_name = new_name
            file.modified_at = datetime.datetime.now()
            s3_bucket_sdk.rename_or_move_file(old_key=old_key, new_key=new_key)
            file.save()
            data = FileSerializer(file).data
            return Response(data, status=200)
        else:
            raise PermissionDenied


class FileMove(APIView):
    def put(self,request,pk,format=None):
        """
        파일 이동
        동일 폴더 이동은 front에서 잡아야해
        """
        if is_owner(request):
            file = get_file(pk)
            if file is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dest_folder_id = request.data['to_folder_id'] if 'to_folder_id' in request.data else None
            if dest_folder_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            dest_folder = get_folder(dest_folder_id)
            if dest_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)


            old_key = file.path
            new_key = file.path = dest_folder.path+file.file_name
            file.parent_folder_id = dest_folder
            file.modified_at = datetime.datetime.now()
            s3_bucket_sdk.rename_or_move_file(old_key=old_key, new_key=new_key)
            file.save()
            data = FileSerializer(file).data
            return Response(data,status=200)
        else:
            raise PermissionDenied


class FolderCreate(APIView):
    def post(self,request,format=None):
        """
        폴더 생성
        """
        if is_owner(request):
            parent_folder_id = request.data['parent_folder_id'] if 'parent_folder_id' in  request.data else None
            if parent_folder_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            folder_name = request.data['folder_name'] if 'folder_name' in  request.data else None
            if folder_name is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            parent_folder = get_folder(parent_folder_id)
            if parent_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            folder_path = parent_folder.path+folder_name+'/'
            folder = Folder.objects.create(path=folder_path, parent_folder_id=parent_folder, folder_name=folder_name)
            data = FolderSerializer(folder).data
            s3_bucket_sdk.create_folder(folder_path)
            return Response(data, status=200)
        else:
            raise PermissionDenied


class FolderRetrieveCopyDelete(APIView):
    def get(self,request,pk,format=None):
        """
        폴더 정보 조회
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is not None:
                fields = request.data['fields'].split(',') if 'fields' in request.data else None
                folder_info_data = FolderSerializer(folder, fields=fields).data
                return Response(folder_info_data, status=200)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise PermissionDenied


    def post(self,request,pk,format=None):
        """
        폴더 복사
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dest_folder_id = request.data['destination_folder_id'] if 'destination_folder_id' in request.data else None
            if dest_folder_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            dest_folder = get_folder(dest_folder_id)
            if dest_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)

            old_key = folder.path
            new_key = dest_folder.path + folder.folder_name + '/'
            s3_bucket_sdk.copy_folder(old_key=old_key, destination_prefix=dest_folder.path, folder_name=folder.folder_name)
            for sub_file in File.objects.filter(path__startswith=old_key):
                if not sub_file.is_trashed:
                    sub_file.path = sub_file.path.replace(old_key, new_key, 1)
                    sub_file.file_id = None
                    sub_file.modified_at = sub_file.created_at = datetime.datetime.now()
                    sub_file.save()
            for sub_folder in Folder.objects.filter(path__startswith=old_key):
                if not sub_folder.is_trashed:
                    sub_folder.path = sub_folder.path.replace(old_key, new_key, 1)
                    sub_folder.folder_id = None
                    sub_folder.modified_at = sub_folder.created_at = datetime.datetime.now()
                    sub_folder.save()

            for sub_folder in Folder.objects.filter(path__startswith=new_key):
                parent_folder_path = sub_folder.path[:sub_folder.path.rfind(sub_folder.folder_name)]
                parent_folder = Folder.objects.get(path=parent_folder_path)
                sub_folder.parent_folder_id = parent_folder
                sub_folder.save()

            for sub_file in File.objects.filter(path__startswith=new_key):
                parent_folder_path = sub_file.path[:sub_file.path.rfind(sub_file.file_name)]
                parent_folder = Folder.objects.get(path=parent_folder_path)
                sub_file.parent_folder_id = parent_folder
                sub_file.save()
            folder = Folder.objects.get(path=new_key)
            data=FolderSerializer(folder).data
            return Response(data,status=200)
        else:
            raise PermissionDenied


    def delete(self,request,pk,format=None):
        """
        폴더 삭제
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            for sub_file in File.objects.filter(path__startswith=folder.path):
                sub_file.is_trashed = True
                sub_file.save()
            for sub_folder in Folder.objects.filter(path__startswith=folder.path):
                sub_folder.is_trashed = True
                sub_folder.save()
            return Response(status=200)
        else:
            raise PermissionDenied


class FolderItemList(APIView):
    def get(self,request,pk,format=None):
        """
        폴더 내 아이템 목록 조회
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            file_fields = request.data['file_fields'].split(',') if 'file_fields' in request.data else None
            folder_fields = request.data['folder_fields'].split(',') if 'folder_fields' in request.data else None
            sort = request.data['sort'] if 'sort' in request.data else None
            limit = request.data['limit'] if 'limit' in request.data else 1000
            if limit>1000:
                limit = 1000
            offset = request.data['offset'] if 'offset' in request.data else 0
            all_items =[]
            if 'sort' == 'name':
                folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id, is_trashed=False).order_by('folder_name')
                file_items = File.objects.filter(parent_folder_id=folder.folder_id,is_trashed=False).order_by('file_name')
            else:
                folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id,is_trashed=False).order_by('created_at')
                file_items = File.objects.filter(parent_folder_id=folder.folder_id,is_trashed=False).order_by('created_at')

            all_items.extend(folder_items)
            all_items.extend(file_items)
            all_items=all_items[offset:offset+limit]
            folder_cnt=0
            for item in all_items:
                if 'Folder' in str(type(item)):
                    folder_cnt+=1

            response_data=OrderedDict()
            response_data['folder_id']=pk
            response_data['file_fields']="all" if 'file_fields' not in request.data else request.data['file_fields']
            response_data['folder_fields'] = "all" if 'folder_fields' not in request.data else request.data['folder_fields']
            response_data['sort'] = "name" if sort =="name" else "date"
            response_data['item_count'] = len(all_items)
            response_data['items']=[]
            response_data['items'].extend(FolderSerializer(all_items[:folder_cnt],fields=folder_fields,many=True).data)
            for i in range(folder_cnt):
                response_data['items'][i].update({'type':'folder'})
                response_data['items'][i].move_to_end('type', last=False)

            response_data['items'].extend(FileSerializer(all_items[folder_cnt:], fields=file_fields, many=True).data)
            for i in range(folder_cnt,len(all_items)):
                response_data['items'][i].update({'type':'file'})
                response_data['items'][i].move_to_end('type', last=False)
            return Response(response_data,status=200)
        else:
            raise PermissionDenied


class FolderRename(APIView):
    def put(self,request,pk,format=None):
        """
        폴더 이름 변경
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            new_folder_name = request.data['new_folder_name'] if 'new_folder_name' in request.data else None
            if new_folder_name is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            old_key = folder.path
            new_key=folder.path = folder.path[:folder.path.rfind(folder.folder_name)] + new_folder_name+'/'
            folder.modified_at = datetime.datetime.now()
            old_folder_name = folder.folder_name
            folder.folder_name = new_folder_name
            s3_bucket_sdk.rename_or_move_folder(old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)
            folder.save()

            for sub_file in File.objects.filter(path__startswith=old_key):
                sub_file.path = sub_file.path.replace(old_key, new_key, 1)
                sub_file.save()
            for sub_folder in Folder.objects.filter(path__startswith=old_key):
                sub_folder.path = sub_folder.path.replace(old_key,new_key,1)
                sub_folder.save()
            data=FolderSerializer(folder).data
            return Response(data,status=200)
        else:
            raise PermissionDenied


class FolderMove(APIView):
    def put(self,request,pk,format=None):
        """
        폴더 이동
        폴더 이동 시 겹치는거 처리가 안됨
        """
        if is_owner(request):
            folder = get_folder(pk)
            if folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dest_folder_id = request.data['destination_folder_id'] if 'destination_folder_id' in request.data else None
            if dest_folder_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            dest_folder = get_folder(dest_folder_id)
            if dest_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            old_key = folder.path
            new_key = folder.path = dest_folder.path + folder.folder_name+'/'
            folder.modified_at = datetime.datetime.now()
            folder.parent_folder_id = dest_folder
            old_folder_name = folder.folder_name
            s3_bucket_sdk.rename_or_move_folder(old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)
            folder.save()
            for sub_file in File.objects.filter(path__startswith=old_key):
                sub_file.path = sub_file.path.replace(old_key,new_key,1)
                sub_file.save()
            for sub_folder in Folder.objects.filter(path__startswith=old_key):
                sub_folder.path = sub_folder.path.replace(old_key, new_key, 1)
                sub_folder.save()
            data= FolderSerializer(folder).data
            return Response(data, status=200)
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