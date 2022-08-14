import logging

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app_api.serializers import (
    GetloclaAndUrlTaskSerializer, GetBoto3TaskSerializer,
    GetCountTasktSerializer, GetTaskResultSerializer
)
from app_api.services import processing_url_file, get_result, processing_boto3

logger = logging.getLogger('api')


class SerializedData:
    serializer_class = None

    def get_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.debug(f'data: {serializer.data}')

        return serializer.data

    def authorization(self, username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is None:
            raise PermissionDenied

        return user


class CsvProcessingBoto3View(GenericAPIView, SerializedData):
    """
    Posting a new job using boto3.
    You need to send a pair of login - password for authorization in the system
    file name in the system or a link to a file hosted in the cloud
    """
    serializer_class = GetBoto3TaskSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request=request)

        user = self.authorization(
            username=data['username'], password=data['password'])

        task = processing_boto3(**data, user=user)

        return Response(task, status=status.HTTP_201_CREATED)


class CsvProcessingView(GenericAPIView, SerializedData):
    """
    Posting a new assignment.
    You need to send a pair of login-password for authorization in the system,
    file name in the system or a link to a file hosted in the cloud
    """
    serializer_class = GetloclaAndUrlTaskSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request=request)

        user = self.authorization(
            username=data['username'], password=data['password'])

        task_id = processing_url_file(
            file_name=data['file_name'],
            file_url=data['file_url'],
            user=user
        )

        return Response({'task_id': task_id}, status=status.HTTP_201_CREATED)


class GetWorkingTasksView(GenericAPIView, SerializedData):
    """
    Get information about pending processes
    You need to send a pair of login and password for authorization in the system
    """
    serializer_class = GetCountTasktSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request=request)

        user = self.authorization(
            username=data['username'], password=data['password'])

        tasks = user.tasks.filter(status='work').count()
        return Response({'tasks': tasks}, status=status.HTTP_200_OK)


class GetResultView(GenericAPIView, SerializedData):
    """
    We get information about the process, or a response.
    You need to send a pair of login - password for authorization in the system
    and task ID
    """
    serializer_class = GetTaskResultSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request=request)

        self.authorization(
            username=data['username'], password=data['password'])

        result = get_result(data['task_id'])

        return Response(result, status=status.HTTP_200_OK)
