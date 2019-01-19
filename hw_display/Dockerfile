FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

# Dependencies needed to build the Motor HAT library
RUN apk add --no-cache \
    gcc \
    linux-headers \
    musl-dev

WORKDIR /app/display
# This is easier than selectively copying in what we want
ADD . .
RUN rm -rf mocks
RUN pip install -r core_requirements.txt -r hw_requirements.txt
