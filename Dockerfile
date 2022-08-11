FROM python:3.10

MAINTAINER Mark Basov
LABEL version="1.0"

WORKDIR /home
COPY . ./


RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 868d6f8e65f9c6163956c8cd051a98c18cfff647

CMD python main.py
>>>>>>> c7e669567621675f4f5fb3f59d078dc59d96351a
