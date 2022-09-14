FROM python:3.10

MAINTAINER Mark Basov
LABEL version="0.1.5-beta"

WORKDIR /home
COPY . ./


RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
