FROM arm32v6/python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/reducer
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
ENTRYPOINT ["python", "-m", "soze_reducer", "-r", "redis://redis:6379/0"]
