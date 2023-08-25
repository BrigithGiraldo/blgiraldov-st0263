import grpc
import files_pb2
import files_pb2_grpc
import os 

SERVER_ADDRESS = os.getenv("HOST_GRPC")
SERVER_PORT = os.getenv("PORT_GRPC")

def list_files():
    with grpc.insecure_channel(f'{SERVER_ADDRESS}:{SERVER_PORT}') as channel:
        for file in files_pb2_grpc.FilesStub(channel).GetFilesList(files_pb2.ListFilesRequest()).files:
            print(file.filename)

if __name__ == '__main__':
    list_files()