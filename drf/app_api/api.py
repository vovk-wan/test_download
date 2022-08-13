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
    Размещаем новое задание используя boto3.
    Нужно отправить пару логин - пароль для авторизации в системе
    имя файла в системе или ссылку на файл размещенный в облаке
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
    Размещаем новое задание.
    Нужно отправить пару логин - пароль для авторизации в системе
    имя файла в системе или ссылку на файл размещенный в облаке
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
    Получаем информацию о незавершенных процессах
    Нужно отправить пару логин - пароль для авторизации в системе
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
    Получаем информацию о процессе, или ответ.
    Нужно отправить пару логин - пароль для авторизации в системе
    и ID задачи
    """
    serializer_class = GetTaskResultSerializer

    def post(self, request, *args, **kwargs):
        data = self.get_data(request=request)

        self.authorization(
            username=data['username'], password=data['password'])

        result = get_result(data['task_id'])

        return Response(result, status=status.HTTP_200_OK)
