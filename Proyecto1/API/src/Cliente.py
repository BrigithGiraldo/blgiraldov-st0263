import requests
import grpc
import file_pb2  
import argparse
import file_pb2_grpc  
import Server_NameNode 
from flask import Flask, request
import os

app = Flask(__name__)

# URL del servidor del NameNode (REST)
name_node_rest_url = "http://172.31.88.26:8080"

def get_file_data_from_user():
    return input(f'Ingrese los datos para el archivo: ').encode('utf-8')

def get_file_data_from_postman(request_data):
    return request_data['file_data'].encode('utf-8')

def write_and_communicate_with_datanode(file_name, file_data):
    try:
        print("write")
        data = {
            "file_name": file_name,
            "file_data": file_data.decode("utf-8")
        }
        response = requests.post(f"{name_node_rest_url}/write", json=data)
        if response.status_code == 200:
            data_node_id = response.json().get("data_node_id")
            data_node_address = response.json().get("data_node_address")
            if not data_node_id or not data_node_address:
                return False, "No se pudo obtener la ubicación del DataNode del NameNode"
        else:
            return False, f"Error al obtener la ubicación del archivo del NameNode: {response.text}"

        channel = grpc.insecure_channel(data_node_address) 
        stub = file_pb2_grpc.DataNodeStub(channel)

        file_message = file_pb2.FileData(file_name=file_name, file_data=file_data)

        response = stub.StoreFile(file_message)

        if response.success:
            return True, f"Archivo se encuentra en DataNode {data_node_id} en {data_node_address}", data_node_id, data_node_address
        else:
            return False, "Error al almacenar el archivo en el DataNode"

    except Exception as e:
        return False, f"Error al escribir o comunicarse con el DataNode: {str(e)}"

def read_and_communicate_with_datanode(file_name):
    try:
        #Obtener la ubicación del archivo desde el NameNode
        print("read")
        response = requests.get(f"{name_node_rest_url}/read/{file_name}")
        if response.status_code == 200:
            data_node_info = response.json().get("data_node_info")
            if not data_node_info:
                return False, "No se pudo obtener la ubicación del DataNode del NameNode"
        else:
            return False, f"Error al obtener la ubicación del archivo del NameNode: {response.text}"

        #Comunicarse con el DataNode para leer el archivo
        print(data_node_info)
        data_node_id = data_node_info["data_node_id"]
        data_node_address = data_node_info["data_node_address"]

        channel = grpc.insecure_channel(data_node_address)
        stub = file_pb2_grpc.DataNodeStub(channel)

        read_request = file_pb2.ReadFileRequest(file_name=file_name)

        response = stub.ReadFile(read_request)

        if response.success:
            return True, response.file_data
        else:
            return False, "Error al leer el archivo desde el DataNode"

    except Exception as e:
        return False, f"Error al leer o comunicarse con el DataNode: {str(e)}"

    
def update_and_communicate_with_datanode(file_name, file_data):
    try:
        #Obtener la ubicación del archivo desde el NameNode
        response = requests.get(f"{name_node_rest_url}/read/{file_name}")
        if response.status_code == 200:
            data_node_info = response.json().get("data_node_info")
            if not data_node_info:
                return False, "No se pudo obtener la ubicación del DataNode del NameNode"
        else:
            return False, f"Error al obtener la ubicación del archivo del NameNode: {response.text}"

        #Comunicarse con el DataNode para actualizar el archivo
        data_node_id = data_node_info["data_node_id"]
        data_node_address = data_node_info["data_node_address"]

        channel = grpc.insecure_channel(data_node_address)
        stub = file_pb2_grpc.DataNodeStub(channel)

        file_message = file_pb2.FileData(file_name=file_name, file_data=file_data)

        response = stub.StoreFile(file_message)

        if response.success:
            return True, f"Archivo actualizado en DataNode {data_node_id} en {data_node_address}"
        else:
            return False, "Error al actualizar el archivo en el DataNode"

    except Exception as e:
        return False, f"Error al actualizar o comunicarse con el DataNode: {str(e)}"


def list_files_from_namenode():
    try:
        response = requests.get(f"{name_node_rest_url}/list_files")
        if response.status_code == 200:
            file_list = response.json()["files"]
            return file_list
        else:
            return []
    except Exception as e:
        return []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cliente de archivo distribuido')
    parser.add_argument('action', type=str, help='Acción a realizar: write, read o update', choices=['write', 'read', 'update', 'list'])
    parser.add_argument('file_name', type=str, help='Nombre del archivo a escribir o leer')
    args = parser.parse_args()

    action = args.action

    if args.file_name:
        file_name = args.file_name
    else:
        file_name = input('Ingrese el nombre del archivo: ')

    # Verificar si la solicitud proviene de Postman o la línea de comandos
    if 'WERKZEUG_RUN_MAIN' in os.environ or 'file_data' in os.environ:
        file_data = get_file_data_from_postman(os.environ)
    else:
        if action == 'write':
            file_data = get_file_data_from_user()
        elif action == 'read':
            file_data = None 
        elif action == 'update':
            file_data = get_file_data_from_user()
        elif action == 'list':
            file_data = None

    # Comunicarse con el DataNode según la acción seleccionada
    if action == 'write':
        write_result = write_and_communicate_with_datanode(file_name, file_data)
        if write_result[0]:
            print(write_result[1])
        else:
            print(f"Error al escribir el archivo: {write_result[1]}")

    elif action == 'read':
        print("Va a hacer un read")
        read_result = read_and_communicate_with_datanode(file_name)
        if read_result[0]:
            print(read_result[1])
        else:
            print(f"Error al leer el archivo: {read_result[1]}")
    
    elif action == 'update':
        update_result = update_and_communicate_with_datanode(file_name, file_data)
        if update_result[0]:
            print(update_result[1])
        else:
            print(f"Error al actualizar el archivo: {update_result[1]}")

    elif action == 'list':
        file_list = list_files_from_namenode()
        if file_list:
            print("Archivos registrados en el sistema:")
            for file_name in file_list:
                print(file_name)
        else:
            print("No se pudieron obtener los archivos registrados.")