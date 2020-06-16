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
import jwt


def get_user_info(request):
    if 'Authorization' in request.headers:
        access_token = request.headers['Authorization'].replace('Bearer ', '')
    else:
        raise PermissionDenied
    if 'X-Cred-Access-Key-Id' in request.headers:
        AWS_ACCESS_KEY_ID = request.headers['X-Cred-Access-Key-Id']
    else:
        raise PermissionDenied
    if 'X-Cred-Secret-Access-Key' in request.headers:
        AWS_SECRET_ACCESS_KEY = request.headers['X-Cred-Secret-Access-Key']
    else:
        raise PermissionDenied
    if 'X-Cred-Session-Token' in request.headers:
        AWS_SESSION_TOKEN = request.headers['X-Cred-Session-Token']
    else:
        raise PermissionDenied
    if 'X-Identity-Id' in request.headers:
        Identity_ID = request.headers['X-Identity-Id']
    else:
        raise PermissionDenied
    
    return Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN


def convert_to_s3_trash_key(Identity_ID, object_suffix):
    return get_trashbox_path(Identity_ID) + object_suffix


def convert_to_s3_key(Identity_ID, logical_path):
    return get_root_path(Identity_ID) + logical_path


def convert_to_logical_path(Identity_ID, s3_key):
    return s3_key.replace(get_root_path(Identity_ID), '')


def get_root_path(Identity_ID):
    return Identity_ID + '/root/'


def get_trashbox_path(Identity_ID):
    return Identity_ID + '/trashbox/'


def get_file(pk, Identity_ID):
    try:
        file = File.objects.get(file_id=pk)
        if Identity_ID not in file.path:
            raise PermissionDenied
        return file
    except ObjectDoesNotExist:
        return None


def get_folder(pk, Identity_ID):
    try:
        folder = Folder.objects.get(folder_id=pk)
        if Identity_ID not in folder.path:
            raise PermissionDenied
        return folder
    except ObjectDoesNotExist:
        return None


def get_trash(pk, Identity_ID):
    try:
        trash = Trash.objects.get(trash_id=pk)
        if Identity_ID not in trash.original_path:
            raise PermissionDenied
        return trash
    except ObjectDoesNotExist:
        return None


def get_object_name(obj_key):
    if obj_key.endswith('/'):
        start_idx = obj_key.rfind('/', 0, len(obj_key) - 1)
        start_idx += 1
        return obj_key[start_idx:len(obj_key) - 1]
    else:
        start_idx = obj_key.rfind('/', 0, len(obj_key))
        start_idx += 1
        return obj_key[start_idx:len(obj_key)]


'''
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
'''


class FileInfoView(APIView):
    def get(self, request, pk, format=None):
        """
        파일 정보 조회
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        file = get_file(pk, Identity_ID)
        if file is not None:
            fields = request.data['fields'].split(',') if 'fields' in request.data else None
            file.path = convert_to_logical_path(file.path)
            file_info_data = FileSerializer(file, fields=fields).data
            return Response(file_info_data, status=200)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FileRetrieveCopyDelete(APIView):
    def get(self, request, pk, format=None):
        """
        다운로드 링크 생성
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        file = get_file(pk, Identity_ID)
        if file is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        response = s3_bucket_sdk.create_presigned_url(s3_client, file.path)
        return Response(response)

    def post(self, request, pk, format=None):
        """
        파일복사
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        source_file = get_file(pk, Identity_ID)
        if source_file is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        dest_folder_id = request.data['to_folder_id'] if 'to_folder_id' in request.data else None
        if dest_folder_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dest_folder = get_folder(dest_folder_id, Identity_ID)
        if dest_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        new_file = deepcopy(source_file)
        new_file.file_id = None
        new_file.created_at = new_file.modified_at = datetime.datetime.now()
        source_key = source_file.path
        if source_file.parent_folder_id.folder_id == dest_folder_id:
            new_file.path += '-복사본'
            new_file.file_name += '-복사본'
            dest_key = new_file.path
        else:
            dest_key = dest_folder.path + source_file.file_name
            new_file.path = dest_key
            new_file.parent_folder_id = dest_folder
            if File.objects.filter(path=dest_key
                                   ).exists():
                File.objects.get(path=dest_key).delete()
        new_file.save()
        new_file.path = convert_to_logical_path(Identity_ID, new_file.path)
        data = FileSerializer(new_file).data
        s3_bucket_sdk.copy_file(s3, source_key, dest_key)
        return Response(data, status=200)

    def delete(self, request, pk, format=None):
        """
        파일 삭제 (휴지통으로)
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        file = get_file(pk, Identity_ID)
        if file is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        trash = Trash.objects.create_trash_by_file(file)
        old_key = file.path
        new_key = get_trashbox_path(request) + file.file_name
        s3_bucket_sdk.rename_or_move_file(s3, old_key=old_key, new_key=new_key)
        file.delete()
        trash.path = convert_to_logical_path(Identity_ID, trash.path)
        data = TrashSerializer(trash).data
        return Response(data, status=200)


class FileUploadLinkCreate(APIView):
    """
    업로드 링크 생성
    """

    def post(self, request, format=None):
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        attributes = request.data['attributes'] if 'attributes' in request.data else None
        if attributes is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'file_name' in attributes:
            file_name = attributes['file_name']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'content_created_at' in attributes:
            content_created_at = attributes['content_created_at']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'content_modified_at' in attributes:
            content_modified_at = attributes['content_modified_at']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'loc_folder_id' in attributes:
            loc_folder_id = attributes['loc_folder_id']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'size' in attributes:
            size = attributes['size']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        parent_folder = get_folder(loc_folder_id, Identity_ID)

        if parent_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        file_key = parent_folder.path + file_name
        file = File.objects.create(content_created_at=content_created_at,
                                   content_modified_at=content_modified_at,
                                   path=file_key,
                                   parent_folder_id=parent_folder,
                                   size=size,
                                   file_name=file_name)

        response = s3_bucket_sdk.create_presigned_post(s3_client, file_key)
        return Response(response)


class FileRename(APIView):
    def put(self, request, pk, format=None):
        """
        파일 이름 변경
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        file = get_file(pk, Identity_ID)
        if file is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        new_name = request.data['new_name'] if 'new_name' in request.data else None
        if new_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        old_key = file.path
        new_key = file.path = file.path[:file.path.rfind(file.file_name)] + new_name
        file.file_name = new_name
        file.modified_at = datetime.datetime.now()
        s3_bucket_sdk.rename_or_move_file(s3, old_key=old_key, new_key=new_key)
        file.save()
        file.path = convert_to_logical_path(Identity_ID, file.path)
        data = FileSerializer(file).data
        return Response(data, status=200)


class FileMove(APIView):
    def put(self, request, pk, format=None):
        """
        파일 이동
        동일 폴더 이동은 front에서 잡아야해
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        file = get_file(pk, Identity_ID)
        if file is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        dest_folder_id = request.data['to_folder_id'] if 'to_folder_id' in request.data else None
        if dest_folder_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dest_folder = get_folder(dest_folder_id, Identity_ID)
        if dest_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        old_key = file.path
        new_key = file.path = dest_folder.path + file.file_name
        file.parent_folder_id = dest_folder
        file.modified_at = datetime.datetime.now()
        s3_bucket_sdk.rename_or_move_file(s3, old_key=old_key, new_key=new_key)
        file.save()
        file.path = convert_to_logical_path(Identity_ID, file.path)
        data = FileSerializer(file).data
        return Response(data, status=200)


class FolderCreate(APIView):
    def post(self, request, format=None):
        """
        폴더 생성
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)

        parent_folder_id = request.data['parent_folder_id'] if 'parent_folder_id' in request.data else None
        if parent_folder_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        folder_name = request.data['folder_name'] if 'folder_name' in request.data else None
        if folder_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        parent_folder = get_folder(parent_folder_id, Identity_ID)
        if parent_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        folder_path = parent_folder.path + folder_name + '/'
        folder = Folder.objects.create(path=folder_path, parent_folder_id=parent_folder, folder_name=folder_name)
        folder.path = convert_to_logical_path(Identity_ID, folder_path)
        data = FolderSerializer(folder).data
        s3_bucket_sdk.create_folder(s3_client, folder_path)
        return Response(data, status=200)


class FolderRetrieveCopyDelete(APIView):
    def get(self, request, pk, format=None):
        """
        폴더 정보 조회
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        folder = get_folder(pk, Identity_ID)
        if folder is not None:
            fields = request.data['fields'].split(',') if 'fields' in request.data else None
            folder.path = convert_to_logical_path(Identity_ID, folder.path)
            folder_info_data = FolderSerializer(folder, fields=fields).data
            return Response(folder_info_data, status=200)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk, format=None):
        """
        폴더 복사
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)

        folder = get_folder(pk, Identity_ID)
        if folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        dest_folder_id = request.data['destination_folder_id'] if 'destination_folder_id' in request.data else None
        if dest_folder_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dest_folder = get_folder(dest_folder_id, Identity_ID)
        if dest_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        old_key = folder.path
        new_key = dest_folder.path + folder.folder_name + '/'
        s3_bucket_sdk.copy_folder(s3, old_key=old_key, destination_prefix=dest_folder.path,
                                  folder_name=folder.folder_name)
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
        folder.path = convert_to_logical_path(Identity_ID, folder.path)
        data = FolderSerializer(folder).data
        return Response(data, status=200)

    def delete(self, request, pk, format=None):
        """
        폴더 삭제
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        folder = get_folder(pk, Identity_ID)
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
        new_key = convert_to_s3_key(Identity_ID, old_key)
        s3_bucket_sdk.rename_or_move_folder(s3, old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)

        folder.delete()
        folder_trash.original_path = convert_to_logical_path(Identity_ID, folder_trash.original_path)
        data = TrashSerializer(folder_trash).data
        return Response(data, status=200)


class FolderItemList(APIView):
    def get(self, request, pk, format=None):
        """
        폴더 내 아이템 목록 조회
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)

        folder = get_folder(pk, Identity_ID)
        if folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        file_fields = request.data['file_fields'].split(',') if 'file_fields' in request.data else None
        folder_fields = request.data['folder_fields'].split(',') if 'folder_fields' in request.data else None
        sort = request.data['sort'] if 'sort' in request.data else None
        limit = request.data['limit'] if 'limit' in request.data else 1000
        if limit > 1000:
            limit = 1000
        offset = request.data['offset'] if 'offset' in request.data else 0
        all_items = []
        if 'sort' == 'name':
            folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id).order_by('folder_name')
            file_items = File.objects.filter(parent_folder_id=folder.folder_id).order_by('file_name')
        else:
            folder_items = Folder.objects.filter(parent_folder_id=folder.folder_id).order_by('created_at')
            file_items = File.objects.filter(parent_folder_id=folder.folder_id).order_by('created_at')

        all_items.extend(folder_items)
        all_items.extend(file_items)
        all_items = all_items[offset:offset + limit]
        folder_cnt = 0
        for item in all_items:
            if 'Folder' in str(type(item)):
                folder_cnt += 1
        for i in range(all_items):
            all_items[i].path = convert_to_logical_path(Identity_ID, all_items[i].path)
        response_data = OrderedDict()
        response_data['folder_id'] = pk
        response_data['file_fields'] = "all" if 'file_fields' not in request.data else request.data['file_fields']
        response_data['folder_fields'] = "all" if 'folder_fields' not in request.data else request.data['folder_fields']
        response_data['sort'] = "name" if sort == "name" else "date"
        response_data['item_count'] = len(all_items)
        response_data['items'] = []
        response_data['items'].extend(FolderSerializer(all_items[:folder_cnt], fields=folder_fields, many=True).data)
        for i in range(folder_cnt):
            response_data['items'][i].update({'type': 'folder'})
            response_data['items'][i].move_to_end('type', last=False)

        response_data['items'].extend(FileSerializer(all_items[folder_cnt:], fields=file_fields, many=True).data)
        for i in range(folder_cnt, len(all_items)):
            response_data['items'][i].update({'type': 'file'})
            response_data['items'][i].move_to_end('type', last=False)
        return Response(response_data, status=200)


class FolderRename(APIView):
    def put(self, request, pk, format=None):
        """
        폴더 이름 변경
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)

        folder = get_folder(pk, Identity_ID)
        if folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        new_folder_name = request.data['new_folder_name'] if 'new_folder_name' in request.data else None
        if new_folder_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        old_key = folder.path
        new_key = folder.path = folder.path[:folder.path.rfind(folder.folder_name)] + new_folder_name + '/'
        folder.modified_at = datetime.datetime.now()
        old_folder_name = folder.folder_name
        folder.folder_name = new_folder_name
        s3_bucket_sdk.rename_or_move_folder(s3, old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)
        folder.save()

        for sub_file in File.objects.filter(path__startswith=old_key):
            sub_file.path = sub_file.path.replace(old_key, new_key, 1)
            sub_file.save()
        for sub_folder in Folder.objects.filter(path__startswith=old_key):
            sub_folder.path = sub_folder.path.replace(old_key, new_key, 1)
            sub_folder.save()
        folder.path = convert_to_logical_path(Identity_ID, folder.path)
        data = FolderSerializer(folder).data
        return Response(data, status=200)


class FolderMove(APIView):
    def put(self, request, pk, format=None):
        """
        폴더 이동
        폴더 이동 시 겹치는거 처리가 안됨
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        folder = get_folder(pk, Identity_ID)
        if folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        dest_folder_id = request.data['destination_folder_id'] if 'destination_folder_id' in request.data else None
        if dest_folder_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dest_folder = get_folder(dest_folder_id, Identity_ID)
        if dest_folder is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        old_key = folder.path
        new_key = folder.path = dest_folder.path + folder.folder_name + '/'
        folder.modified_at = datetime.datetime.now()
        folder.parent_folder_id = dest_folder
        old_folder_name = folder.folder_name
        s3_bucket_sdk.rename_or_move_folder(s3, old_key=old_key, old_folder_name=old_folder_name, new_key=new_key)
        folder.save()
        for sub_file in File.objects.filter(path__startswith=old_key):
            sub_file.path = sub_file.path.replace(old_key, new_key, 1)
            sub_file.save()
        for sub_folder in Folder.objects.filter(path__startswith=old_key):
            sub_folder.path = sub_folder.path.replace(old_key, new_key, 1)
            sub_folder.save()
        folder.path = convert_to_logical_path(Identity_ID, folder.path)
        data = FolderSerializer(folder).data
        return Response(data, status=200)


def expire_trash(Identity_ID):
    trashes = Trash.objects.filter(expire_time__lte=datetime.datetime.now(), cascade_trash=None,
                                   original_path__startswith=Identity_ID)
    for trash in trashes:
        trash.delete()


class TrashList(APIView):
    """
    버린 아이템 목록 조회
    file_fields, folder_fields적용안할 예정
    """

    def get(self, request, format=None):
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        expire_trash()
        file_fields = request.data['file_fields'].split(',') if 'file_fields' in request.data else None
        folder_fields = request.data['folder_fields'].split(',') if 'folder_fields' in request.data else None
        sort = request.data['sort'] if 'sort' in request.data else None
        limit = request.data['limit'] if 'limit' in request.data else 1000
        if limit > 1000:
            limit = 1000
        offset = request.data['offset'] if 'offset' in request.data else 0
        if 'sort' == 'name':
            trashes = Trash.objects.filter(cascade_trash=None, original_path__startswith=Identity_ID).order_by('obj_name')
        else:
            trashes = Trash.objects.filter(cascade_trash=None, original_path__startswith=Identity_ID).order_by('trashed_at')
        trashes = trashes[offset:offset + limit]
        for i in range(len(trashes)):
            trashes[i].original_path = convert_to_logical_path(Identity_ID, trashes[i].original_path)
        trashed_item_count = len(trashes)

        response_data = OrderedDict()
        response_data['file_fields'] = "all" if 'file_fields' not in request.data else request.data['file_fields']
        response_data['folder_fields'] = "all" if 'folder_fields' not in request.data else request.data[
            'folder_fields']
        response_data['sort'] = "name" if sort == "name" else "date"
        response_data['trashed_item_count'] = trashed_item_count
        response_data['trashed_items'] = TrashSerializer(trashes, many=True).data

        return Response(response_data, status=200)


def get_parent_folder_path(obj):
    if 'file_name' in obj:
        return obj.path[:obj.path.rfind(obj.file_name)]
    else:
        return obj.path[:obj.path.rfind(obj.folder_name)]


def middle_folder_create(obj, s3_client):
    is_end = False
    while not is_end:
        key = get_parent_folder_path(obj)
        try:
            parent = Folder.objects.get(path=key)
            obj.parent_folder_id = parent
            obj.save()
            is_end = True
        except ObjectDoesNotExist:
            parent = Folder.objects.create(path=key, parent_folder_id=None, folder_name=get_object_name(key))
            s3_bucket_sdk.create_folder(s3_client, parent.path)
            obj.parent_folder_id = parent
            obj.save()
            obj = parent


class TrashControl(APIView):
    def put(self, request, pk, format=None):
        """
        버린 아이템 복구
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)

        trash = get_trash(pk, Identity_ID)
        if trash is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if trash.type == "file":
            if trash.cascade_trash is not None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recovered_file = File.objects.create(content_created_at=trash.content_created_at,
                                                 content_modified_at=trash.content_modified_at,
                                                 created_at=trash.created_at,
                                                 modified_at=trash.modified_at,
                                                 path=trash.original_path,
                                                 parent_folder_id=None,
                                                 size=trash.size,
                                                 file_name=trash.obj_name
                                                 )
            s3_bucket_sdk.rename_or_move_file(s3, old_key=get_trashbox_path(Identity_ID) + trash.obj_name,
                                              new_key=recovered_file.path)
            middle_folder_create(recovered_file, s3_client)
            recovered_file.save()
            recoverd_file.path = convert_to_logical_path(Identity_ID, recovered_file)
            data = FileSerializer(recovered_file).data
        else:
            if trash.cascade_trash is not None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                recovered_parent_folder = Folder.objects.get(path=trash.original_path)
            except ObjectDoesNotExist:
                recovered_parent_folder = Folder.objects.create(created_at=sub_trash.created_at,
                                                                modified_at=datetime.datetime.now(),
                                                                path=sub_trash.original_path,
                                                                parent_folder_id=None,
                                                                size=sub_trash.size,
                                                                folder_name=sub_trash.obj_name)
                s3_bucket_sdk.create_folder(s3_client, recovered_parent_folder.path)
                middle_folder_create(recovered_parent_folder, s3_client)
            for sub_trash in Trash.objects.filter(cascade_trash=trash, type='folder', original_path__startswith=Identity_ID):
                try:
                    Folder.objects.get(path=sub_trash.original_path)

                except ObjectDoesNotExist:
                    recovered_folder = Folder.objects.create(created_at=sub_trash.created_at,
                                                             modified_at=datetime.datetime.now(),
                                                             path=sub_trash.original_path,
                                                             parent_folder_id=None,
                                                             size=sub_trash.size,
                                                             folder_name=sub_trash.obj_name)
                    s3_bucket_sdk.create_folder(s3_client, recovered_folder.path)
            for sub_trash in Trash.objects.filter(cascade_trash=trash, type='folder', original_path__startswith=Identity_ID):
                recovered_folder = Folder.objects.get(path=sub_trash.original_path)
                parent_folder = Folder.objects.get(
                    path=recovered_folder.path[:recovered_folder.path.rfind(recoverd_folder.folder_name)])
                recovered_folder.parent_folder_id = parent_folder
                recovered_folder.save()

            for sub_trash in Trash.objects.filter(cascade_trash=trash, type='file', original_path__startswith=Identity_ID):
                recovered_file = File.objects.create(content_created_at=sub_trash.content_created_at,
                                                     content_modified_at=sub_trash.content_modified_at,
                                                     created_at=sub_trash.created_at,
                                                     modified_at=datetime.datetime.now(),
                                                     path=sub_trash.original_path,
                                                     parent_folder_id=None,
                                                     size=sub_trash.size,
                                                     file_name=sub_trash.file_name
                                                     )
                recovered_file.parent_folder_id = Folder.objects.get(
                    path=recovered_file.path[:recovered_file.path.rfind(recovered_file.file_name)])
                recovered_file.save()

                s3_bucket_sdk.rename_or_move_file(s3, old_key=get_trashbox_path(Identity_ID) + sub_trash.obj_name,
                                                  new_key=recovered_file.path)
            recovered_parent_folder.path = convert_to_logical_path(Identity_ID, recovered_parent_folder.path)
            data = FolderSerializer(recovered_parent_folder).data
        trash.delete()
        return Response(data, status=200)

    def delete(self, request, pk, format=None):
        """
        버린 아이템 완전 삭제
        """
        Identity_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN = get_user_info(request)
        s3, s3_client = s3_bucket_sdk.get_s3_and_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
        trash = get_trash(pk, Identity_ID)
        if trash is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if trash.cascade_trash is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        s3_bucket_sdk.remove_file(s3, get_trashbox_path(Identity_ID) + trash.obj_name)
        trash.delete()
        return Response(status=200)
