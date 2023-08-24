import os
from concurrent import futures
import grpc

import files_pb2
import files_pb2_grpc

from dotenv import load_dotenv

load_dotenv()

ROOT_PATH = os.getenv("ROOT_PATH")
PORT = os.getenv("PORT")


class ListFilesServicer(files_pb2_grpc.FilesServicer):

    def GetFilesList(self, request, context):
        print(f"Request: {request}")
        files = []
        for item in os.listdir(ROOT_PATH):
            item_path = os.path.join(ROOT_PATH, item)
            if os.path.isfile(item_path):
                files.append(files_pb2.File(filename=item, file=bytes(item, encoding="utf-8")))
        response = files_pb2.ListFilesResponse(files=files)
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    files_pb2_grpc.add_FilesServicer_to_server(ListFilesServicer(), server)
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f'Servidor en ejecución en el puerto {PORT}...')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()