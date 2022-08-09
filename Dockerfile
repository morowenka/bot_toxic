FROM python:3.10.2

MAINTAINER by Mark Basov
LABEL version="1.0"

WORKDIR /home
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt
CMD python main.py
