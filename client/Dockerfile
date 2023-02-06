FROM python:3.9

RUN pip install paho-mqtt
RUN pip install numpy
RUN pip install pandas

COPY client/mqtt_client.py /app/mqtt_client.py

CMD ["python", "/app/mqtt_client.py"]
