from gunicorn.config import User

from app_api.models import Task
from app_api.tasks import (
    for_url_file_process, local_file_process, boto3_file_process)
from django_RF_AO_IOT.celery import app


def processing_boto3(file_name: str, access_key: str, secret_key: str,
                     region_name: str, bucket_name: str, endpoint_url: str,
                     user: User, **kwargs) -> dict:
    task_pk = Task.objects.create(user=user)

    task = boto3_file_process.delay(
        task_pk=task_pk.pk,
        file_name=file_name,
        access_key=access_key,
        secret_key=secret_key,
        region_name=region_name,
        bucket_name=bucket_name,
        endpoint_url=endpoint_url
    )

    return {'task_id': task.id}


def processing_url_file(file_name: str, file_url: str, user) -> list[str]:
    task_id = []
    if file_url:
        task_pk = Task.objects.create(user=user)
        task = for_url_file_process.delay(
            task_pk=task_pk.pk, url=file_url)
        task_id.append(task.id)
    if file_name:
        task_pk = Task.objects.create(user=user)
        task = local_file_process.delay(
            task_pk=task_pk.pk, file_name=file_name)
        task_id.append(task.id)

    return task_id


def get_result(task_id: str) -> dict:
    task = app.AsyncResult(task_id)

    if task.status == 'FAILURE':
        return {'result': 'FAILURE'}

    if task.ready():
        task_data: dict = task.get()
        return {'result': task_data}

    return {'result': 'in process'}
