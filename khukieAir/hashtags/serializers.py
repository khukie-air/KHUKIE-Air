from rest_framework import serializers
from .models import HashTag

class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ['file_id', 'hashtags_count', 'hashtag', 'created_at']