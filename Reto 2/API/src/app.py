from flask import Flask, jsonify, request
import grpc
import os 
import pika
import productor
import uuid
import json
import files_pb2, files_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

host_rmq = os.getenv("HOST_RMQ")
rmq_port = os.getenv('PORT_RMQ')
rmq_user = os.getenv('USER')
rmq_password = os.getenv('PASSWORD')

@app.route('/buscar-archivo')
def search_files():
    print("entró aquí app")
    query = request.args.get('query')
    producer = productor.ArchivoMOM()
    data = producer.call(query)
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/archivos")
def list_files():
    with grpc.insecure_channel(f'{os.getenv("HOST_GRPC")}:{os.getenv("PORT_GRPC")}') as channel:
        list_files_client = files_pb2_grpc.FilesStub(channel)
        response = list_files_client.GetFilesList(files_pb2.ListFilesRequest())
        return jsonify({"files": [file.filename for file in response.files]})

if __name__ == '__main__':
    app.run(host='0.0.0.0')