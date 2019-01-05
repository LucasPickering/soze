FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/soze/display
ADD . .
RUN pip install -r requirements.txt
RUN pip install Adafruit-Motor-HAT-Python-Library/
