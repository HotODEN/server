import asyncio
from concurrent import futures
import subprocess
import grpc
from protocol import api_pb2_grpc
from protocol import api_pb2

class SLAM():
    process = None
    def __init__(self):
        self.process = subprocess.Popen(
            ['./build/main',
             'ORB_SLAM2/Vocabulary/ORBvoc.txt', 'slam/TUM.yaml'],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        while True:
            r = self.process.stdout.readline()
            print(r)
            if r == b'INITIALIZED\n':
                break



class APIServicer(api_pb2_grpc.APIServicer):

    slam_pool = []

    SLAM_POOL_SIZE = 1

    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

        for _ in range(self.SLAM_POOL_SIZE):
            loop.run_in_executor(None, self.add_slam_pool)


    def add_slam_pool(self):
        self.slam_pool += [SLAM()]

    def get_slam_from_pool(self):
        if not self.slam_pool:
            return SLAM()

        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.add_slam_pool)
        return self.slam_pool.pop()

    def GetInfo(self, request, context):
        return api_pb2.Info(version="0.1.0")

    def Track(self, request_iterator, context):

        print("track init\n")

        print(request_iterator.__next__())

        yield(api_pb2.Update())

        pass

def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  api_pb2_grpc.add_APIServicer_to_server(
      APIServicer(), server)
  server.add_insecure_port('[::]:8080')
  server.start()
  server.wait_for_termination()

if __name__ == "__main__":
    print("Starting server...\n")

    serve()
