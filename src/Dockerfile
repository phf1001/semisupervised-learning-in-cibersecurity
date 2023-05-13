FROM python:3.10.7-slim-buster

WORKDIR /usr/src/semisupervised-learning-in-cibersecurity

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/semisupervised-learning-in-cibersecurity/requirements.txt
RUN pip install -r requirements.txt

COPY .. /usr/src/semisupervised-learning-in-cibersecurity