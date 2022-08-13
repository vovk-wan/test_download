from rest_framework import serializers


class GetTaskResultSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class GetCountTasktSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class GetloclaAndUrlTaskSerializer(serializers.Serializer):
    file_url = serializers.URLField(required=False, allow_blank=True)
    file_name = serializers.CharField(
        max_length=250, required=False, allow_blank=True)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

    def validate(self, attrs):
        if attrs.get('file_name') or attrs.get('file_url'):
            return attrs
        raise serializers.ValidationError(
                                        detail='at least one of the fields '
                                        'file name or file URL must be filled'
                                        )


class GetBoto3TaskSerializer(serializers.Serializer):
    access_key = serializers.CharField(max_length=150)
    secret_key = serializers.CharField(max_length=150)
    region_name = serializers.CharField(max_length=50)
    endpoint_url = serializers.URLField()
    bucket_name = serializers.CharField(max_length=150)
    file_name = serializers.CharField(max_length=250)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

