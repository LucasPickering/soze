FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/soze/display
ADD . .
RUN pip install redis
RUN pip install -e mocks/*
