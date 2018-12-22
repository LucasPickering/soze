FROM python:3-alpine

WORKDIR /app/soze

ADD core core
ADD server server

RUN pip install -e core
RUN pip install -e server

WORKDIR /app/soze/server
