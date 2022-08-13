import json
import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView

from app_api.models import Task
from app_api.serializers import (
    GetloclaAndUrlTaskSerializer, GetBoto3TaskSerializer)
from app_api.tasks import (
    local_file_process, boto3_file_process, for_url_file_process)
from django_RF_AO_IOT.celery import app

logging.basicConfig()
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


class GetResultView(GenericAPIView):
    serializer_class = GetloclaAndUrlTaskSerializer

    """
    Получаем информацию о процессе, или ответ
    Размещаем новое задание.
    Нужно отправить пару логин - пароль для авторизации в системе
    и ID задачи
    """
    def post(self, request, *args, **kwargs):
        request_data: str = request.body.decode('utf-8')
        try:
            data: dict = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(f'{self.__class__.__qualname__}, exception: {err}')
            return JsonResponse({'result': 'fail'}, status=status.HTTP_400_BAD_REQUEST)

        request_id: int = data.get('request_id')

        task = app.AsyncResult(request_id)
        if task.status == 'FAILURE':
            return JsonResponse({'results': 'FAILURE'}, status=status.HTTP_200_OK)
        if task.ready():
            task_data: dict = task.get()
            return JsonResponse({'results': task_data}, status=status.HTTP_200_OK)
        return JsonResponse({'result': 'wait'}, status=status.HTTP_200_OK)