# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /myApp

COPY requirements.txt requirements.txt

# OpenCV dependencies
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip3 install -r requirements.txt

COPY . .

# For Production
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:30001", "wsgi:app"]

# # For Development
# ENV FLASK_APP=main.py
# CMD ["flask", "run", "--host=0.0.0.0"]