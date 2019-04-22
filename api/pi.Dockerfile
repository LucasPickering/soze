FROM arm32v6/python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/api
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .

ENTRYPOINT [ "flask", "run", "--host=0.0.0.0" ]
