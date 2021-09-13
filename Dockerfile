FROM python:3.9

COPY ./online /app
COPY ./shared /app/shared
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "./server.py"]
