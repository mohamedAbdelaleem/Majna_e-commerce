FROM python:3.10-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    postgresql-dev \
    libjpeg-turbo-dev \
    zlib-dev \
    postgresql-client

COPY ./src/requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src /usr/src/app