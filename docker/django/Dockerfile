FROM python:3.10-alpine

COPY ./src /usr/src/app
COPY ./docker/django/entrypoint.sh /usr/src/entrypoint.sh
COPY ./docker/setup_initial_data.sql /usr/src/setup_initial_data.sql

WORKDIR /usr/src/app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    postgresql-dev \
    libjpeg-turbo-dev \
    zlib-dev \
    postgresql-client

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/src/entrypoint.sh"]