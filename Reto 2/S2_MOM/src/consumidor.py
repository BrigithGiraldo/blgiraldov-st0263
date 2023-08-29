import pika
import os
from dotenv import load_dotenv
import time

load_dotenv()

rmq_host = os.getenv('HOST_RMQ')
rmq_port = os.getenv('PORT_RMQ')
rmq_user = os.getenv('USER')
rmq_password = os.getenv('PASSWORD')
rmq_queue = os.getenv('QUEUE')

time.sleep(5)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host, 
                                                                port=int(rmq_port),
                                                                credentials= pika.PlainCredentials(username=rmq_user,password=rmq_password)))
channel = connection.channel()

channel.queue_declare(queue=rmq_queue)
print("Se hace la conexión")

channel.basic_qos(prefetch_count=1)

def on_request(ch, method, props, body):
    filename = body.decode()
    print("Solicitud recibida para:", filename)
    response = buscar_archivo(filename)
    print("Respuesta generada")
    ch.basic_ack(delivery_tag=method.delivery_tag) 

def buscar_archivo(filename):
    print("Buscando archivo:", filename)
    for root, dirs, files in os.walk(os.getcwd()):
        print("Entrando en el directorio:", root)
        if filename in files:
            return f"El archivo {filename} se encuentra en el microservicio."
    return f"No se ha encontrado el archivo {filename} en el microservicio."

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=rmq_queue, on_message_callback=on_request)

print("Esperando por solicitudes...")
channel.start_consuming()