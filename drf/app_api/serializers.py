from rest_framework import serializers
from django.conf import settings

class GetTaskSerializer(serializers.Serializer):
    file_path = serializers.FilePathField(path=settings.BASE_DIR)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

# GetTaskSerializer