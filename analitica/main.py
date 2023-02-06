import pika
import os
import math
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class Analytics():
    max_value = -math.inf
    min_value = math.inf
    dias_value = 0
    prom_value = 0
    sumatoria_value = 0
    dias_mas_cienmil_pasos_value = 0
    dias_menos_cincomil_pasos_value = 0
    pasos_anteriores_value =0
    dias_mejorados_consecutivos=0

    #variables de control
    
    influx_bucket = 'rabbit'
    influx_token = 'token-secreto'
    influx_url = 'http://influx:8086'
    influx_org = 'org'

    
    
    def write_db(self, tag, key, value):
        client= InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point('Analytics').tag("Descriptive", tag).field(key, value)
        write_api.write(bucket=self.influx_bucket, record=point)

    #### codigo para configurar la lectura 
    #### valor maximo 
    def add_max_value(self, _medida):
        if _medida > self.max_value:
            self.max_value = _medida
             
        print("Max :{}".format(self.max_value), flush=True)  
        self.write_db( "pasos", "pasos_maximos", self.max_value)
        
    ###· valor minimo        

    def add_min_value(self, _medida):
        if _medida < self.min_value:
            self.min_value = _medida
        print("Min :{}".format(self.min_value), flush=True)
        self.write_db( "pasos", "pasos_minimos", self.min_value)

    # promedio
    def add_prom_value(self, _medida):
        self.dias_value+=1
        self.sumatoria_value+=_medida
        self.prom_value=self.sumatoria_value/self.dias_value
        print("Prom : {}".format(self.prom_value), flush=True)
        self.write_db( "pasos", "promedio", self.prom_value)
        
    
    # dias con mas de cien mil pasos
    def add_dias_cienk_pasos_value(self, _medida):
        if _medida>100000:
            self.dias_mas_cienmil_pasos_value+=1
        print("Dias con mas de 100000 pasos : {}".format(self.dias_mas_cienmil_pasos_value), flush=True)
        self.write_db( "pasos", "dias_mas_cienmil", self.dias_mas_cienmil_pasos_value)
    
     # dias con menos de cinco mil pasos
    def add_dias_cincok_pasos_value(self, _medida):
        if _medida<5000:
            self.dias_menos_cincomil_pasos_value+=1
        print("Dias con menos de 5000 pasos : {}".format(self.dias_menos_cincomil_pasos_value), flush=True)
        self.write_db( "pasos", "dias_menos_cincomil", self.dias_menos_cincomil_pasos_value)
    
     # dias mejorados consecutivos
    def add_dias_consecutivos_mejorados_value(self, _medida):
        if _medida>self.pasos_anteriores_value:
            self.dias_mejorados_consecutivos+=1
        else:
            self.dias_mejorados_consecutivos=0

        self.pasos_anteriores_value=_medida
        print("Dias consecutivos mejorados : {}".format(self.dias_mejorados_consecutivos), flush=True)
        self.write_db( "pasos", "dias_mejorados_consecutivos", self.dias_mejorados_consecutivos)
        print("\n\r\n\r", flush=True)

        
    def take_measurement(self, _mensaje):
        mensaje = _mensaje.split("=")
        medida = float(mensaje[-1])
        print("medida {}".format(medida))
        self.add_max_value(medida)
        self.add_min_value(medida)
        self.add_prom_value(medida)
        self.add_dias_cienk_pasos_value(medida)
        self.add_dias_cincok_pasos_value(medida)
        self.add_dias_consecutivos_mejorados_value(medida)

        








if __name__ == '__main__':
    #variable global 
    analitica = Analytics()

    def callback(ch, method, properties, body):
        global analitica
        mensaje = body.decode("utf-8")
        #print("mensaje del servidor {}".format(mensaje), flush=True)
        analitica.take_measurement(mensaje)

    url = os.environ.get('AMQP_URL','amqp://user:pass@rabbit:5672/%2f')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='pasos')
    channel.queue_bind(exchange = 'amq.topic',queue='pasos',routing_key="#")
    channel.basic_consume(queue='pasos', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()