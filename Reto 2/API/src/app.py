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
host_grpc = os.getenv("HOST_GRPC")

rmq_port = os.getenv('PORT_RMQ')
rmq_user = os.getenv('USER')
rmq_password = os.getenv('PASSWORD')

grpc_port = os.getenv("PORT_GRPC")


@app.route('/search-files')
def search_files():
    query = request.args.get('query')
    producer = productor.ArchivoMOM()
    data = producer.call(query)
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/files")
def list_files():
    with grpc.insecure_channel(f'{host_grpc}:{grpc_port}') as channel:
        list_files_client = files_pb2_grpc.FilesStub(channel)

        response = list_files_client.GetFilesList(files_pb2.ListFilesRequest())

        return jsonify({"files": [file.filename for file in response.files]})


if __name__ == '__main__':
    app.run(host='0.0.0.0')