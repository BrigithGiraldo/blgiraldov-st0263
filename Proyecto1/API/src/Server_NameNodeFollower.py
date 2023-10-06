import grpc
import file_pb2
import file_pb2_grpc
from concurrent import futures
from flask import Flask, request, jsonify

app = Flask(__name__)

leader_address = "localhost:50051"

class NameNodeFollowerServicer(file_pb2_grpc.NameNodeServicer):
    def GetFileLocation(self, request, context):
        try:
            channel = grpc.insecure_channel(leader_address)
            stub = file_pb2_grpc.NameNodeStub(channel)
            response = stub.GetFileLocation(request)
            return response

        except Exception as e:
            return file_pb2.GetFileLocationResponse(
                success=False,
                message=str(e)
            )

def communicate_with_leader(request):
    try:
        channel = grpc.insecure_channel(leader_address)
        stub = file_pb2_grpc.NameNodeStub(channel)
        response = stub.RegisterDataNode(request)
        return response

    except Exception as e:
        return file_pb2.RegisterDataNodeResponse(
            message=str(e)
        )

@app.route('/write', methods=['POST'])
def write_file():
    try:
        data = request.get_json()
        file_name = data['file_name']
        file_data = data['file_data'].encode('utf-8')
        
        request = file_pb2.RegisterDataNodeRequest(
            data_node_id="follower", 
            data_node_address="follower",
        )
        response = communicate_with_leader(request)

        if response.message == "DataNode registrado con éxito":
            return jsonify({"message": "Archivo se almacenará en el NameNode principal"})
        else:
            return jsonify({"error": "Error al registrar el DataNode en el NameNode principal"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/read/<file_name>', methods=['GET'])
def read_file(file_name):
    try:
        request = file_pb2.GetFileLocationRequest(file_name=file_name)
        channel = grpc.insecure_channel(leader_address)
        stub = file_pb2_grpc.NameNodeStub(channel)
        response = stub.GetFileLocation(request)

        if response.success:
            return jsonify({
                "message": "Archivo se encuentra en DataNode",
                "data_node_id": response.data_node_id,
                "data_node_address": response.data_node_address
            })
        else:
            return jsonify({"error": response.message}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        return jsonify({"message": "Función no disponible en el NameNodeFollower"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_NameNodeServicer_to_server(NameNodeFollowerServicer(), server)
    server.add_insecure_port('[::]:50052') 
    server.start()

    app.run(host='0.0.0.0', port=8081)  
