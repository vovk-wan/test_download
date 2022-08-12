from rest_framework import serializers
from django.conf import settings


class GetloclaAndUrlTaskSerializer(serializers.Serializer):
    file_name = serializers.FilePathField(path=settings.BASE_DIR)
    file_url = serializers.URLField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class GetUrlTaskSerializer(serializers.Serializer):
    file_url = serializers.URLField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

class GetBoto3TaskSerializer(serializers.Serializer):
    access_key = serializers.URLField()
    secret_key = serializers.URLField()
    region_name = serializers.URLField()
    endpoint_s3_url = serializers.URLField()
    bucket_name = serializers.URLField()
    file_name = serializers.URLField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
