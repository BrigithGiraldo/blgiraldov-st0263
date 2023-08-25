import pika
import uuid
from dotenv import load_dotenv
import os

rmq_host = os.getenv('HOST_RMQ')
rmq_port = os.getenv('PORT_RMQ')
rmq_user = os.getenv('USER')
rmq_password = os.getenv('PASSWORD')
rmq_queue = os.getenv('QUEUE')

class ArchivoMOM:

    def __init__(self):
        self.connection =  pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host, 
                                                                port=int(rmq_port),
                                                                credentials= pika.PlainCredentials(username=rmq_user,password=rmq_password)))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
    
    def call(self, filename):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='search_files',
            routing_key='archivo_rpc',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=filename)
        while self.response is None:
            self.connection.process_data_events()
        return self.response.decode()
