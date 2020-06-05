from rest_framework import serializers
from hashtags.models import HashTag

class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ['sort', 'hashtags_count', 'hashtag']