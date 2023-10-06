import grpc
import file_pb2
import file_pb2_grpc
from concurrent import futures
import uuid
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

file_storage = {}

# Dirección del servidor del NameNode (gRPC)
name_node_grpc_address = "172.31.88.26:50051"

data_node_id = str(uuid.uuid4())

data_nodes = {}  


def register_with_namenode():
    try:
        # Comunicación con el NameNode a través de gRPC para registrarse
        channel = grpc.insecure_channel(name_node_grpc_address)
        stub = file_pb2_grpc.NameNodeStub(channel)
        response = stub.RegisterDataNode(file_pb2.RegisterDataNodeRequest(
            data_node_id=data_node_id,
            data_node_address=app.config["data_node_address"]
        ))
        return response.message
    except Exception as e:
        return str(e)
        
def inform_file_location_to_namenode(file_name):
    try:
        # Comunicación con el NameNode a través de gRPC para informar la ubicación del archivo
        channel = grpc.insecure_channel(name_node_grpc_address)
        stub = file_pb2_grpc.NameNodeStub(channel)
        response = stub.InformFileLocation(file_pb2.InformFileLocationRequest(
            file_name=file_name,
            data_node_id=data_node_id
        ))
        return response.message
    except Exception as e:
        return str(e)

def communicate_with_datanode(data_node_id, file_name, file_data):
    try:
        if data_node_id in data_nodes:
            data_node_address = data_nodes[data_node_id]
            channel = grpc.insecure_channel(data_node_address)
            stub = file_pb2_grpc.DataNodeStub(channel)
            response = stub.StoreFile(file_pb2.FileData(file_name=file_name, file_data=file_data))
            return response.success, data_node_id, data_node_address
        else:
            return False, "DataNode no encontrado"

    except Exception as e:
        return False, str(e)

class DataNodeServicer(file_pb2_grpc.DataNodeServicer):
    def StoreFile(self, request, context):
        file_name = request.file_name
        file_data = request.file_data

        file_storage[file_name] = file_data

        inform_message = inform_file_location_to_namenode(file_name)
        print(inform_message)

        return file_pb2.StoreFileResponse(success=True, message="Archivo almacenado con éxito")

    def ReadFile(self, request, context):
        file_name = request.file_name

        if file_name in file_storage:
            file_data = file_storage[file_name]
            return file_pb2.ReadFileResponse(success=True, file_data=file_data)
        else:
            return file_pb2.ReadFileResponse(success=False, message="Archivo no encontrado")

    def UpdateFile(self, request, context):
        file_name = request.file_name
        print(file_name)
        file_data = request.file_data
        print(file_data)

        if file_name in file_storage:
            file_storage[file_name] = file_data
            return file_pb2.StoreFileResponse(success=True, message="Archivo actualizado con éxito")
        else:
            return file_pb2.StoreFileResponse(success=False, message="Archivo no encontrado")

if __name__ == '__main__':

    app.config["data_node_address"] = f"localhost:8080"

    data_nodes[data_node_id] = app.config["data_node_address"]

    register_message = register_with_namenode()
    print(register_message)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_DataNodeServicer_to_server(DataNodeServicer(), server)
    server.add_insecure_port(app.config["data_node_address"])
    server.start()

    app.run(host='0.0.0.0', port=8080)