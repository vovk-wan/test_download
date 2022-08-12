import codecs
import csv
import logging
from typing import Iterator

import boto3
import botocore.exceptions
import requests
import requests.exceptions
from celery.backends import cache

from app_api.models import Task
from django.conf import settings

from django_RF_AO_IOT.celery import app
from celery.utils.log import get_task_logger

TEST_MODE = True

logger = get_task_logger('serveces')
if TEST_MODE:
    logger.setLevel('INFO')
# logging.warning()
ACCESS_KEY = 'YCAJEi_BYVBsymk-7eqKUQan4'
SECRET_KEY = 'YCPA-2WX7_XlboVLIOXZv0eMjQoNbI-vkldW5Bl8'
REGION_NAME = 'ru-central1'
BUCKET_NAME = 'vovkvan'
ENDPOINT_S3_URL = 'https://storage.yandexcloud.net'
FILES_PATH = settings.BASE_DIR/'files'


def parsing_csv(csv_obj: Iterator, filename: str) -> dict[str, float]:
    """
    The function reads data from a file and sums every tenth column
    :param csv_obj: csv file of specified format
    :type csv_obj: Iterator
    :param filename: filename for the process
    :type filename: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    reader = csv.reader(csv_obj)
    row = next(reader)
    cols = next(csv.reader(row))
    col_name = cols[10::10]
    len_cols = len(col_name)
    summ = [0] * len_cols
    for index, row in enumerate(reader, 1):
        try:
            next_row = next(csv.reader(row))[10::10]
            next_row = list(map(float, next_row))
        except (ValueError, TypeError) as err:
            next_row = [0] * len_cols
            logger.warning(
                f'file name: {filename}, str №: {index}, error: {err}')
        except StopIteration as err:
            next_row = [0] * len_cols
            logger.error(f' todo {err}')

        summ = list(map(sum, zip(summ, next_row)))
    return {col_name: col_sum for col_name, col_sum in zip(col_name, summ)}


@app.task(bind=True)
def boto3_file_process(
        self, task_pk: int, file_name: str, access_key: str,
        secret_key: str, region_name: str, bucket_name: str,
        endpoint_url: str) -> dict[str, float]:
    """
    Function to download files from s3 storage using boto3
    :param self celery task
    :param task_pk: task id in bd
    :type task_pk: int
    :param file_name: filename in bucket
    :type file_name: str
    :param access_key: access key from account
    :type access_key: str
    :param secret_key: secret key from account
    :type secret_key: str
    :param region_name: region name
    :type region_name: str
    :param bucket_name: bucket name in storage
    :type bucket_name: str
    :param endpoint_url: endpoint for s3 storage
    :type endpoint_url: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    logger.info(
        f'start host: {self.request.hostname}, '
        f'args: {self.request.args}, '
        f'kwargs: {self.request.kwargs}'
    )
    try:
        session = boto3.session.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

        s3 = session.client(
            service_name='s3',
            endpoint_url=endpoint_url
        )
        data = s3.get_object(Bucket=bucket_name, Key=file_name)
        csv_obj = codecs.getreader('utf-8')(data['Body'])
        result = parsing_csv(csv_obj=csv_obj, filename=file_name)
        Task.objects.filter(pk=task_pk).update(status='finished')
    except (botocore.exceptions.EndpointConnectionError,) as err:
        logger.error(err)
        result = {'error': 'file not found'}
        Task.objects.filter(pk=task_pk).update(status='failed')
    return result


@app.task(bind=True)
def for_url_file_process(self, task_pk: int, url: str) -> dict[str, float]:
    """
    Function to download files by url storage using requests
    :param self celery task
    :param task_pk: task id in bd
    :type task_pk: int
    :param url: File URL
    :type url: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    logger.info(
        f'start host: {self.request.hostname}'
        f'args: {self.request.args}, '
        f'kwargs: {self.request.kwargs}'
    )
    try:
        with requests.get(url, stream=True, timeout=5) as r:
            csv_obj = (line.decode('utf-8') for line in r.iter_lines())
            Task.objects.filter(pk=task_pk).update(status='finished')
            result = parsing_csv(csv_obj=csv_obj, filename=url)
    except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema,
            requests.exceptions.ConnectionError
            ) as err:
        logger.error(err)
        result = {'error': 'file not found'}
        Task.objects.filter(pk=task_pk).update(status='failed')

    return result


@app.task(bind=True)
def local_file_process(self, task_pk: int, file_name: str) -> dict[str, float]:
    """
    Function to download files from local hard drive
    :param self celery task
    :param task_pk: task id in bd
    :type task_pk: int
    :param file_name: File URL
    :type file_name: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    logger.info(
        f'start host: {self.request.hostname}, '
        f'args: {self.request.args}, '
        f'kwargs: {self.request.kwargs}'
    )
    try:
        with open(FILES_PATH/file_name, 'r', encoding='utf8') as csv_file:
            result = parsing_csv(csv_obj=csv_file, filename=file_name)
        Task.objects.filter(pk=task_pk).update(status='finished')
    except (FileNotFoundError, IsADirectoryError)as err:
        logger.error(err)
        result = {'error': 'file not found'}
        Task.objects.filter(pk=task_pk).update(status='failed')
    return result
