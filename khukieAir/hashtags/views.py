from django.shortcuts import render
from .models import HashTag
from .serializers import HashTagSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied

class HashTagCreateInquire(APIView):
    """
    Create hashtag or Inquire the entire of hashtags
    """
    def get(self, request, format=None):
        hashtags = HashTag.objects.all()
        serializer = HashTagSerializer(hashtags, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HashTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return PermissionDenied

class HashTagRetrieveDelete(APIView):
    """
    Retrieve detailed data of hashtag or Delete hashtag
    """
    def get_object(self, pk):
        try:
            return HashTag.objects.get(pk=pk)
        except HashTag.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        hashtag = self.get_object(pk)
        serializer = HashTagSerializer(hashtag)
        return Response(serializer.data)

    def delete(self, requests, pk, format=None):
        hashtag = self.get_object(pk)
        hashtag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

