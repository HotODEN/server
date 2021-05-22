from concurrent import futures
import grpc
from protocol import api_pb2_grpc
from protocol import api_pb2

class APIServicer(api_pb2_grpc.APIServicer):

    def GetInfo(self, request, context):
        return api_pb2.Info(version="0.1.0")


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  api_pb2_grpc.add_APIServicer_to_server(
      APIServicer(), server)
  server.add_insecure_port('[::]:8080')
  server.start()
  server.wait_for_termination()

if __name__ == "__main__":
    print ("Starting server...")

    serve()
    # application.listen(8080)
    # tornado.ioloop.IOLoop.current().start()
