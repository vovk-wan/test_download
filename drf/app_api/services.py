import codecs
import csv
import logging
from typing import Iterator

import boto3
import requests

from django_RF_AO_IOT.celery import app
ACCESS_KEY = 'YCAJEi_BYVBsymk-7eqKUQan4'
SECRET_KEY = 'YCPA-2WX7_XlboVLIOXZv0eMjQoNbI-vkldW5Bl8'
REGION_NAME = 'ru-central1'
BUCKET_NAME = 'vovkvan'
ENDPOINT_S3_URL = 'https://storage.yandexcloud.net'


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
            logging.error(
                f'file name: {filename}, str №: {index}, error: {err}')
        except StopIteration as err:
            next_row = [0] * len_cols
            logging.error(f'косяк {err}')

        summ = list(map(sum, zip(summ, next_row)))
    return {col_name: col_sum for col_name, col_sum in zip(col_name, summ)}


@app.task
def aws_s3_file_process(
        file_name: str, access_key: str, secret_key: str, region_name: str,
        bucket_name: str, endpoint_url: str) -> dict[str, float]:
    """
    Function to download files from s3 storage using boto3
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

    return parsing_csv(csv_obj=csv_obj, filename=file_name)


@app.task
def aws_s3_for_url_file_process(url: str) -> dict[str, float]:
    """
    Function to download files by url storage using requests
    :param url: File URL
    :type url: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    with requests.get(url, stream=True) as r:
        csv_obj = (line.decode('utf-8') for line in r.iter_lines())
        return parsing_csv(csv_obj=csv_obj, filename=url)


@app.task
def local_file_process(file_name: str) -> dict[str, float]:
    """
    Function to download files from local hard drive
    :param file_name: File URL
    :type file_name: str
    :return: sum of every tenth column
    :rtype: dict[str, float]
    """
    with open(file_name, 'r', encoding='utf8') as csv_file:
        return parsing_csv(csv_obj=csv_file, filename=file_name)


def create_big_file(file_name: str) -> dict:
    with open(file_name, 'r', encoding='utf8') as csv_file:
        hat = csv_file.readline()
        body = csv_file.readlines()
        with open('data_test.csv', mode='w', encoding='utf8') as file_write:
            file_write.writelines(hat)
            for _ in range(3000):
                file_write.writelines(body)
                file_write.flush()



if __name__ == '__main__':
    # print(local_file_process('../data.csv'))
    # AWS_file_process('data.csv')
    # create_big_file('../data1.csv')
    a = aws_s3_file_process(
        access_key=ACCESS_KEY, secret_key=SECRET_KEY, region_name=REGION_NAME,
        bucket_name='vovkvan', file_name='data.csv', endpoint_url=ENDPOINT_S3_URL )
    print(a)
    # a = aws_s3_file_process(
    #     access_key=ACCESS_KEY, secret_key=SECRET_KEY, region_name=REGION_NAME,
    #     bucket_name=BUCKET_NAME, filename='https://storage.yandexcloud.net/vovkvan/data.csv', endpoint_url=ENDPOINT_S3_URL)
    # print(a)

    a = {'col9': 81.13102168233925, 'col19': 89.07842935269687, 'col29': 80.94699954936576, 'col39': 88.21018612209457, 'col49': 86.59565362695817}
    b = {'col9': 81.13102168233925, 'col19': 89.07842935269687, 'col29': 80.94699954936576, 'col39': 88.21018612209457, 'col49': 86.59565362695817}