from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .models import File, Folder, Trash
from . import s3_bucket_sdk
from .serializers import FileSerializer, FolderSerializer, TrashSerializer
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

def get_user_pk(reqeust):
    return str(1)
def get_root_path(request):
    return get_user_pk(request)+'/root/'

def get_trashbox_path(request):
    return get_user_pk(request)+'/trashbox/'

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


def get_trash(pk):
    try:
        trash = Trash.objects.get(trash_id=pk)
        return trash
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
            trash = Trash.objects.create_trash_by_file(file)
            old_key = file.path
            new_key = get_trashbox_path(request)+file.file_name
            s3_bucket_sdk.rename_or_move_file(old_key=old_key, new_key=new_key)
            file.delete()
            data=TrashSerializer(trash).data
            return Response(data, status=200)
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
            attributes =  request.data['attributes'] if 'attributes' in request.data else None
            if attributes is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if 'file_name' in attributes:
                file_name=attributes['file_name']
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if 'content_created_at' in attributes:
                content_created_at=attributes['content_created_at']
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if 'content_modified_at' in attributes:
                content_modified_at=attributes['content_modified_at']
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if 'loc_folder_id' in attributes:
                loc_folder_id=attributes['loc_folder_id']
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if 'size' in attributes:
                size=attributes['size']
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            parent_folder = get_folder(loc_folder_id)

            if parent_folder is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            file_key = parent_folder.path+file_name
            file=File.objects.create(content_created_at=content_created_at,
                                     content_modified_at=content_modified_at,
                                     path=file_key,
                                     parent_folder_id=parent_folder,
                                     size=size,
                                     file_name=file_name)


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
                sub_file.path = sub_file.path.replace(old_key, new_key, 1)
                sub_file.file_id = None
                sub_file.modified_at = sub_file.created_at = datetime.datetime.now()
                sub_file.save()
            for sub_folder in Folder.objects.filter(path__startswith=old_key):
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
            folder_trash = Trash.objects.create_trash_by_folder(folder)
            for sub_file in File.objects.filter(path__startswith=folder.path):
                sub_file_trash = Trash.objects.create_trash_by_file(sub_file)
                sub_file_trash.cascade_trash = folder_trash
                sub_file_trash.save()
            for sub_folder in Folder.objects.filter(path__startswith=folder.path):
                if folder.folder_id != sub_folder.folder_id:
                    sub_folder_trash = Trash.objects.create_trash_by_folder(sub_folder)
                    sub_folder_trash.cascade_trash = folder_trash
                    sub_folder_trash.save()
            old_key = folder.path
            old_folder_name = folder.folder_name
            new_key = get_trashbox_path(request)+folder.folder_name+'/'
            s3_bucket_sdk.rename_or_move_folder(old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)

            folder.delete()
            data = TrashSerializer(folder_trash).data
            return Response(data,status=200)
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
                folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id).order_by('folder_name')
                file_items = File.objects.filter(parent_folder_id=folder.folder_id).order_by('file_name')
            else:
                folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id).order_by('created_at')
                file_items = File.objects.filter(parent_folder_id=folder.folder_id).order_by('created_at')

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


def expire_trash():
    return

class TrashList(APIView):
    """
    버린 아이템 목록 조회
    file_fields, folder_fields적용안할 예정
    """
    def get(self,request,format=None):
        if is_owner(request):
            file_fields = request.data['file_fields'].split(',') if 'file_fields' in request.data else None
            folder_fields = request.data['folder_fields'].split(',') if 'folder_fields' in request.data else None
            sort = request.data['sort'] if 'sort' in request.data else None
            limit = request.data['limit'] if 'limit' in request.data else 1000
            if limit > 1000:
                limit = 1000
            offset = request.data['offset'] if 'offset' in request.data else 0
            if 'sort' == 'name':
                trashes = Trash.objects.filter(cascade_trash=None).order_by('obj_name')
            else:
                trashes = Trash.objects.filter(cascade_trash=None).order_by('trashed_at')
            trashes = trashes[offset:offset + limit]
            trashed_item_count = len(trashes)

            response_data = OrderedDict()
            response_data['file_fields'] = "all" if 'file_fields' not in request.data else request.data['file_fields']
            response_data['folder_fields'] = "all" if 'folder_fields' not in request.data else request.data[
                'folder_fields']
            response_data['sort'] = "name" if sort == "name" else "date"
            response_data['trashed_item_count'] = trashed_item_count
            response_data['trashed_items'] = TrashSerializer(trashes, many=True).data

            return Response(response_data, status=200)
        else:
            raise PermissionDenied

def get_parent_folder_path(obj):
    if 'file_name' in obj:
        return obj.path[:obj.path.rfind(obj.file_name)]
    else:
        return obj.path[:obj.path.rfind(obj.folder_name)]

def middle_folder_create(obj):
    next_obj=obj
    is_end = False
    while not is_end:
        key = get_parent_folder_path(next_obj)
        parent = Folder.objects.get(path=key)
        if parent is not None:
            next_obj.parent_folder_id = parent
            next_obj.save()
            is_end=True
        else:
            parent = Folder.objects.create(path=key,parent_folder_id=None,folder_name=get_object_name(key))
            s3_bucket_sdk.create_folder(parent.path)
            next_obj.parent_folder_id=parent
            next_obj.save()
            next_obj=parent


def delete_trash(pk):
    trash = get_trash(pk)
    if trash is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if trash.cascade_trash is not None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    trash.delete()
    return Response(status=200)


class TrashControl(APIView):
    def put(self,request,pk,format=None):
        """
        버린 아이템 복구
        """
        if is_owner(request):
            trash = get_trash(pk)
            if trash is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if trash.type =="file":
                recovered_file = File.objects.create(content_created_at=trash.content_created_at,
                                                     content_modified_at=trash.content_modified_at,
                                                     created_at = trash.created_at,
                                                     modified_at = trash.modified_at,
                                                     path=trash.original_path,
                                                     parent_folder_id=None,
                                                     size=trash.size,
                                                     file_name=trash.obj_name
                                                     )
                s3_bucket_sdk.rename_or_move_file(old_key=get_trashbox_path(request)+trash.obj_name,new_key=recovered_file.path)
                middle_folder_create(recovered_file)
                recovered_file.save()
                data= FileSerializer(recovered_file).data
            else:
                if trash.cascade_trash is not None:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                for sub_trash in Trash.objects.filter(cascade_trash=trash, type='folder'):
                    try:
                        Folder.objects.get(path=sub_trash.original_path)
                        recoved_folder = Folder.objects.create(created_at=sub_trash.created_at,
                                                               modified_at=datetime.datetime.now(),
                                                               path=sub_trash.original_path,
                                                               parent_folder_id=None,
                                                               size=sub_trash.size,
                                                               folder_name=sub_trash.obj_name)
                        s3_bucket_sdk.create_folder(recoved_folder.path)
                    except ObjectDoesNotExist:
                        continue
                for sub_trash in Trash.objects.filter(cascade_trash=trash, type='folder'):
                    recovered_folder = Folder.objects.get(path=sub_trash.original_path)
                    parent_folder = Folder.objects.get(path=recovered_folder.path[:recovered_folder.path.rfind(recoverd_folder.folder_name)])
                    recovered_folder.parent_folder_id = parent_folder
                    recovered_folder.save()

                for sub_trash in Trash.objects.filter(cascade_trash=trash, type='file'):
                    recovered_file = File.objects.create(content_created_at=sub_trash.content_created_at,
                                                         content_modified_at=sub_trash.content_modified_at,
                                                         created_at=sub_trash.created_at,
                                                         modified_at=datetime.datetime.now(),
                                                         path=sub_trash.original_path,
                                                         parent_folder_id=None,
                                                         size=sub_trash.size,
                                                         file_name=sub_trash.file_name
                                                        )
                    recovered_file.parent_folder_id = Folder.objects.get(path=recovered_file.path[:recovered_file.path.rfind(recovered_file.file_name)])
                    recovered_file.save()
                    s3_bucket_sdk.rename_or_move_file(old_key=get_trashbox_path(request)+sub_trash.obj_name,new_key=recovered_file.path)
                middle_folder_create(trash)
            trash.delete()
            return Response(data,status=200)
        else:
            raise PermissionDenied

    def delete(self,request,pk,format=None):
        """
        버린 아이템 완전 삭제
        """
        if is_owner(request):
            return delete_trash(pk)
        else:
            raise PermissionDenied