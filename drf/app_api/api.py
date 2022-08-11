import json
import logging

from django_RF_AO_IOT.celery import app

from django.http import JsonResponse
from rest_framework.generics import GenericAPIView

from app_api.serializers import GetTaskSerializer
from app_api.services import local_file_process, aws_s3_file_process


# @method_decorator(csrf_exempt, name='dispatch')
class CsvProcessingView(GenericAPIView):
    """
    Размещаем новое задание.
    Нужно отправить пару логин - пароль для авторизации в системе
    имя файла в системе или ссылку на файл размещенный в облаке AWS
    """
    serializer_class = GetTaskSerializer

    def post(self, request, *args, **kwargs):

        request_data = request.body.decode('utf8')
        # logger.info(f'{self.__class__.__qualname__}, before json request_data: {request_data}')
        try:
            data = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(err)
            return JsonResponse({'result': 'fail'}, status=400)
        file_path: str = data.get('file_path')
        task = aws_s3_file_process if file_path.startswith('http') else local_file_process
        result = task.delay(file_name=file_path)

        return JsonResponse({'result': result.id}, status=200)


# @method_decorator(csrf_exempt, name='dispatch')
class GetResultView(GenericAPIView):
    serializer_class = GetTaskSerializer

    """Попробуем получить информацию о процессе, или ответ"""
    def post(self, request, *args, **kwargs):
        request_data: str = request.body.decode('utf-8')
        try:
            data: dict = json.loads(request_data)
        except (AttributeError, json.decoder.JSONDecodeError) as err:
            logging.error(f'{self.__class__.__qualname__}, exception: {err}')
            return JsonResponse({'result': 'fail'}, status=400)

        request_id: int = data.get('request_id')

        task = app.AsyncResult(request_id)
        if task.status == 'FAILURE':
            return JsonResponse({'results': 'FAILURE'}, status=200)
        if task.ready():
            task_data: dict = task.get()
            return JsonResponse({'results': task_data}, status=200)
        return JsonResponse({'result': 'wait'}, status=200)