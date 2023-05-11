# pull official base image
FROM python:3.10.7-slim-buster

# set work directory
WORKDIR /usr/src/semisupervised-learning-in-cibersecurity

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y netcat
RUN pip install --upgrade pip
RUN pwd
COPY requirements.txt /usr/src/semisupervised-learning-in-cibersecurity/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY .. /usr/src/semisupervised-learning-in-cibersecurity