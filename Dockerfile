# syntax=docker/dockerfile:1

# gitminer reads config.json from mounted volume and writes output to /logs dir

# Base Image
FROM python:3.9-slim-buster

# Environment Variables
ENV LANG en_US.UTF-8
ENV LC_ALL "${LANG}"
ENV PATH /app:$PATH

# Setting Working Directory
WORKDIR /app

# Install Dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy Application (exclude config.json)
COPY ./gitminer.py .

# Entrypoint allows parameters to be passed on docker run
ENTRYPOINT [ "python3", "gitminer.py" ]
