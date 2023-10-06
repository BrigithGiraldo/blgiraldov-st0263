import grpc
import file_pb2
import file_pb2_grpc
from concurrent import futures
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

data_nodes = {} 

file_locations = {}  

class NameNodeServicer(file_pb2_grpc.NameNodeServicer):
    def RegisterDataNode(self, request, context):
        try:
            data_node_id = request.data_node_id
            data_node_address = request.data_node_address
            data_nodes[data_node_id] = data_node_address
            print("DataNode registrado:", data_node_id, data_node_address)
            return file_pb2.RegisterDataNodeResponse(message="DataNode registrado con éxito")
        except Exception as e:
            return file_pb2.RegisterDataNodeResponse(message=str(e))
    
    def GetFileLocation(self, request, context):
        file_name = request.file_name

        if file_name in file_locations:
            leader_data_node_id, follower_data_node_id = file_locations[file_name]

            if (leader_data_node_id in data_nodes) and (follower_data_node_id in data_nodes):
                leader_data_node_address = data_nodes[leader_data_node_id]
                follower_data_node_address = data_nodes[follower_data_node_id]

                return file_pb2.GetFileLocationResponse(
                    success=True,
                    leader_data_node_id=leader_data_node_id,
                    leader_data_node_address=leader_data_node_address,
                    follower_data_node_id=follower_data_node_id,
                    follower_data_node_address=follower_data_node_address
                )
            else:
                return file_pb2.GetFileLocationResponse(
                    success=False,
                    message="DataNode líder o seguidor no encontrado"
                )
        else:
            return file_pb2.GetFileLocationResponse(
                success=False,
                message="Archivo no encontrado"
            )
    
    def InformFileLocation(self, request, context):
        try:
            file_name = request.file_name
            data_node_id = request.data_node_id


            if data_node_id in data_nodes:
                data_node_address = data_nodes[data_node_id]

                if file_name in file_locations:
                    leader_data_node_id, follower_data_node_id = file_locations[file_name]
                    if (leader_data_node_id != data_node_id) and (follower_data_node_id != data_node_id):
                        file_locations[file_name] = [data_node_id, follower_data_node_id]
                else:

                    data_node_ids = list(data_nodes.keys())
                    data_node_ids.remove(data_node_id) 
                    random.shuffle(data_node_ids)
                    new_follower_data_node_id = data_node_ids[0]
                    file_locations[file_name] = [data_node_id, new_follower_data_node_id]

                return file_pb2.InformFileLocationResponse(
                    success=True,
                    message=f"Ubicación de archivo '{file_name}' actualizada en DataNode líder {data_node_id} y seguidor {file_locations[file_name][1]}"
                )
            else:
                return file_pb2.InformFileLocationResponse(
                    success=False,
                    message="DataNode no encontrado"
                )
        except Exception as e:
            return file_pb2.InformFileLocationResponse(
                success=False,
                message=str(e)
            )

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

@app.route('/write', methods=['POST'])
def write_file():
    print("Entra write")
    try:
        data = request.get_json()
        file_name = data['file_name']
        print(file_name)
        file_data = data['file_data'].encode('utf-8')
        print(file_data)
        
        data_node_id = random.choice(list(data_nodes.keys()))
        data_node_address = data_nodes[data_node_id]
        response = communicate_with_datanode(data_node_id, file_name, file_data)
        print(response)
        if response[0]:
            data_node_id = response[1]
            data_node_address = response[2]
            print(response)
            return jsonify({"message": "Archivo se almacenará en DataNode", "data_node_id": data_node_id, "data_node_address": data_node_address})
        else:
            return jsonify({"error": response[1]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/read/<file_name>', methods=['GET'])
def read_file(file_name):
    print("Entra read")
    try:
        if file_name in file_locations:
            leader_data_node_id, follower_data_node_id = file_locations[file_name]

            if leader_data_node_id in data_nodes:
                leader_data_node_info = {
                    "data_node_id": leader_data_node_id,
                    "data_node_address": data_nodes[leader_data_node_id]
                }
                return jsonify({
                    "message": "Archivo se encuentra en DataNode líder",
                    "data_node_info": leader_data_node_info
                })
            elif follower_data_node_id in data_nodes:
                follower_data_node_info = {
                    "data_node_id": follower_data_node_id,
                    "data_node_address": data_nodes[follower_data_node_id]
                }
                return jsonify({
                    "message": "Archivo se encuentra en DataNode seguidor",
                    "data_node_info": follower_data_node_info
                })
            else:
                return jsonify({"error": "Ningún DataNode registrado para el archivo"}), 500
        else:
            return jsonify({"error": "Archivo no encontrado"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        file_list = list(file_locations.keys())
        return jsonify({"files": file_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_NameNodeServicer_to_server(NameNodeServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    app.run(host='172.31.88.26', port=8080)
