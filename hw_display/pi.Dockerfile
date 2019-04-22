FROM arm32v6/python:3-alpine

ENV PYTHONUNBUFFERED=1

# Dependencies needed to build the Motor HAT library
RUN apk add --no-cache \
    gcc \
    linux-headers \
    musl-dev

WORKDIR /app/display
ADD core_requirements.txt \
    hw_requirements.txt \
    ./
ADD Adafruit-Motor-HAT-Python-Library Adafruit-Motor-HAT-Python-Library
RUN pip install -r core_requirements.txt -r hw_requirements.txt
ADD soze_display soze_display

ENTRYPOINT [ "python", "-m", "soze_display", "-r", "redis://redis:6379/0" ]
