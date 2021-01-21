# For both dev and production

FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/api
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .

CMD ["flask", "run", "--host=0.0.0.0"]
