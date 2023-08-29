import grpc
import files_pb2
import files_pb2_grpc
import os 
import os
from dotenv import load_dotenv

load_dotenv()

def list_files():
    with grpc.insecure_channel(f'{os.getenv("HOST_GRPC")}:{os.getenv("PORT_GRPC")}') as channel:
        for file in files_pb2_grpc.FilesStub(channel).GetFilesList(files_pb2.ListFilesRequest()).files:
            print(file.filename)

if __name__ == '__main__':
    list_files()