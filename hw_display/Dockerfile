# For development use w/ mocked hardware only

FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/display
ADD . .
RUN pip install -r core_requirements.txt
RUN pip install -e mocks/

CMD [ "python", "-m", "soze_display", "-r", "redis://redis:6379/0" ]
