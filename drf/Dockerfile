FROM python:3.10-slim

RUN apt-get update && \
    apt-get -y install libpq-dev gcc

WORKDIR /app

ADD requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    pip install psycopg2 && \
    python3 -m pip install --no-cache-dir -r requirements.txt

ADD . .
