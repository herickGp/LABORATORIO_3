FROM python:3.9.16

WORKDIR /app

RUN apt-get update
RUN pip install influxdb-client==1.36
RUN pip install pika==1.3.1

COPY analitica/main.py /app/main.py

CMD [ "python", "/app/main.py" ]