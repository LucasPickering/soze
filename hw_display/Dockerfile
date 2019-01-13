FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

# Dependencies needed to build the Motor HAT library
RUN apk add --no-cache \
    gcc \
    linux-headers \
    musl-dev

WORKDIR /app/soze/display
ADD . .
RUN pip install -r requirements.txt
RUN pip install -e Adafruit-Motor-HAT-Python-Library/
