FROM python:3.10

MAINTAINER Mark Basov
LABEL version="1.0"

WORKDIR /home
COPY . ./

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
