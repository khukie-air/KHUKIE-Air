from django.db import models

# Create your models here.

class HashTag(models.Model):
    sort = models.CharField(default = "files")
    hashtags_count = models.IntegerField(default = 0)
    hashtag = models.CharField(max_length=100, blank=True, default='')