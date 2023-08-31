from flask import Flask, jsonify, request
import grpc
import os 
import pika.exceptions
import productor
import uuid
import json
import files_pb2, files_pb2_grpc
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

host_rmq = os.getenv("HOST_RMQ")
rmq_port = os.getenv("PORT_RMQ")
rmq_user = os.getenv("USER")
rmq_password = os.getenv("PASSWORD")

@app.route('/buscar-archivo')
def search_files():
    query = request.args.get('query')
    
    try:
        with grpc.insecure_channel(f'{os.getenv("HOST_GRPC")}:{os.getenv("PORT_GRPC")}') as channel:
            list_files_client = files_pb2_grpc.FilesStub(channel)
            response = list_files_client.GetFilesList(files_pb2.ListFilesRequest())
            found = any(file.filename == query for file in response.files)
            if found:
                data = {"message": f"El archivo '{query}' se encuentra en el microservicio usando gRPC."}
            else:
                data = {"message": f"No se ha encontrado el archivo '{query}' en el microservicio usando gRPC."}
    except grpc.RpcError as e:
        print("Error en gRPC, intentando con MOM:", e)
        producer = productor.ArchivoMOM()
        data = producer.call(query)
        if "No se ha encontrado el archivo" in data:
            data = {"message": f"No se ha encontrado el archivo '{query}' en el microservicio usando gRPC ni MOM."}
        else:
            data = {"message": f"El archivo '{query}' se encuentra en el microservicio usando MOM."}
    except pika.exceptions.AMQPError as e:
        print("Error en MOM:", e)
        data = {"error": "No se pudo completar la búsqueda de archivos."}

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