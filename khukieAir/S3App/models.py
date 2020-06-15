from django.db import models
import datetime
#time zone설정해야될듯

class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    content_created_at=models.DateTimeField()
    content_modified_at=models.DateTimeField()
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    path=models.TextField()
    parent_folder_id= models.ForeignKey('Folder', on_delete=models.CASCADE, null=True)
    size=models.PositiveIntegerField()
    file_name=models.CharField(max_length=255)

class Folder(models.Model):
    folder_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    path = models.TextField() #text? slug?
    parent_folder_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True) #ondelete 알아볼것
    size = models.PositiveIntegerField(default=0)
    folder_name = models.CharField(max_length=255)

class TrashManager(models.Manager):
    def create_trash_by_file(self, file):
        trash = self.create(original_path=file.path, type='file', content_created_at=file.content_created_at,
                            content_modified_at=file.content_modified_at, created_at=file.created_at,
                            modified_at=file.modified_at, size=file.size, obj_name=file.file_name)
        trash.expire_time = trash.trashed_at+datetime.timedelta(days=30)
        return trash

    def create_trash_by_folder(self, folder):
        trash = self.create(original_path=folder.path, type='folder', created_at=folder.created_at,
                            modified_at=folder.modified_at, size=folder.size, obj_name=folder.folder_name)
        return trash


class Trash(models.Model):
    trash_id = models.AutoField(primary_key = True)
    original_path = models.TextField()
    cascade_trash = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    type = models.CharField(max_length=6)
    trashed_at = models.DateTimeField(auto_now_add=True)
    expire_time = models.DateTimeField(default=None,null=True)
    content_created_at = models.DateTimeField(default=None,null=True)
    content_modified_at = models.DateTimeField(default=None,null=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    size = models.PositiveIntegerField()
    obj_name = models.CharField(max_length=256)

    objects = TrashManager()
'''
[Reference]
Django model fields : https://docs.djangoproject.com/en/3.0/ref/models/fields/
Diff between auto_now and autu_now_add : https://tomining.tistory.com/145
Diff CharField and TextField : https://itmining.tistory.com/125
Diff blank vs null : https://wayhome25.github.io/django/2017/09/23/django-blank-null/
'''