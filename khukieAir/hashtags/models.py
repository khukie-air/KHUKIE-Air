from django.db import models
import json


# Create your models here.

class HashTag(models.Model):
    file_id = models.CharField(max_length=100)
    hashtags_count = models.IntegerField(default = 0)
    hashtag = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now=True)

    def set_file_id(self, id):
        self.file_id = json.dumps(id)

    def set_hashtag(self, tag):
        self.hashtag = json.dups(tag)