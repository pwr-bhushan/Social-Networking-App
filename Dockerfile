FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN  apt-get update

COPY . /social_app/

WORKDIR /social_app/

RUN pip install -r requirements.txt