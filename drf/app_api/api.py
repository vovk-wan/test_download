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


class CsvProcessingBoto3View(GenericAPIView):
    """
    Размещаем новое задание используя boto3.
    Нужно отправить пару логин - пароль для авторизации в системе
    имя файла в системе или ссылку на файл размещенный в облаке
    """
    serializer_class = GetBoto3TaskSerializer

    def post(self, request, *args, **kwargs):

        request_data = request.body.decode('utf8')
        logger.info(
            f'{self.__class__.__qualname__}, '
            f'before json request_data: {request_data}'
        )
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(err)
            return JsonResponse(
                {'result': 'fail'}, status=status.HTTP_400_BAD_REQUEST)
        username: str = data.get('username')
        password: str = data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse(
                {'result': 'failed authorization'},
                status=status.HTTP_403_FORBIDDEN
            )
        file_name: str = data.get('file_name')
        access_key: str = data.get('access_key')
        secret_key: str = data.get('secret_key')
        region_name: str = data.get('region_name')
        bucket_name: str = data.get('bucket_name')
        endpoint_s3_url: str = data.get('endpoint_s3_url')
        result = []

        if file_name:
            task_pk = Task.objects.create(user=user)
            task = boto3_file_process.delay(
                task_pk=task_pk.pk, file_name=file_name, access_key=access_key,
                secret_key=secret_key, region_name=region_name,
                bucket_name=bucket_name, endpoint_url=endpoint_s3_url)
            result.append(task.id)

        return JsonResponse({'task_id': result}, status=status.HTTP_200_OK)


class CsvProcessingView(GenericAPIView):
    """
    Размещаем новое задание.
    Нужно отправить пару логин - пароль для авторизации в системе
    имя файла в системе или ссылку на файл размещенный в облаке
    """
    serializer_class = GetloclaAndUrlTaskSerializer

    def post(self, request, *args, **kwargs):

        request_data = request.body.decode('utf8')
        logger.info(
            f'{self.__class__.__qualname__}, '
            f'before json request_data: {request_data}'
        )
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(err)
            return JsonResponse(
                {'result': 'fail'}, status=status.HTTP_400_BAD_REQUEST
            )
        username: str = data.get('username')
        password: str = data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse(
                {'result': 'failed authorization'},
                status=status.HTTP_403_FORBIDDEN
            )
        file_name: str = data.get('file_name')
        file_url: str = data.get('file_url')
        result = []
        if file_url:
            task_pk = Task.objects.create(user=user)
            task = for_url_file_process.delay(
                                            task_pk=task_pk.pk, url=file_url)
            result.append(task.id)
        if file_name:
            task_pk = Task.objects.create(user=user)
            task = local_file_process.delay(
                                       task_pk=task_pk.pk, file_name=file_name)
            result.append(task.id)

        return JsonResponse({'task_id': result}, status=status.HTTP_200_OK)


class GetWorkingTasksView(GenericAPIView):
    """
    Получаем информацию о незавершенных процессах
    Нужно отправить пару логин - пароль для авторизации в системе
    """
    serializer_class = GetloclaAndUrlTaskSerializer

    def post(self, request, *args, **kwargs):
        request_data: str = request.body.decode('utf-8')
        try:
            data: dict = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(f'{self.__class__.__qualname__}, exception: {err}')
            return JsonResponse(
                {'result': 'fail'}, status=status.HTTP_400_BAD_REQUEST)
        username: str = data.get('username')
        password: str = data.get('password')
        user: User = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse(
                {'result': 'failed authorization'},
                status=status.HTTP_403_FORBIDDEN
            )
        tasks = user.tasks.filter(status='work').count()
        return JsonResponse({'tasks': tasks}, status=status.HTTP_200_OK)


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