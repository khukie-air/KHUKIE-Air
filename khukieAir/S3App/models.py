from django.db import models


class File(models.Model):
    id = models.AutoField(primary_key=True)
    content_created_at=models.DateTimeField()
    content_modified_at=models.DateTimeField()
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    path=models.FilePathField()
    parent_folder_id= models.ForeignKey('Folder', on_delete=models.CASCADE)
    size=models.PositiveIntegerField()
    file_name=models.CharField(max_length=255)
    is_trashed = models.BooleanField(default=False)

class Folder(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    path = models.FilePathField() #text? slug?
    parent_folder_id = models.ForeignKey('self', on_delete=models.DO_NOTHING) #ondelete 알아볼것
    size = models.PositiveIntegerField(default=0)
    folder_name = models.CharField(max_length=255)
    is_trashed = models.BooleanField(default=False)

class Trash(models.Model):
    id = models.AutoField(primary_key = True)
    trashed_at = models.DateTimeField(auto_now_add=True)

'''
[Reference]
Django model fields : https://docs.djangoproject.com/en/3.0/ref/models/fields/
Diff between auto_now and autu_now_add : https://tomining.tistory.com/145
Diff CharField and TextField : https://itmining.tistory.com/125
Diff blank vs null : https://wayhome25.github.io/django/2017/09/23/django-blank-null/
'''