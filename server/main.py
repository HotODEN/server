import asyncio
from concurrent import futures
import subprocess
import grpc
import sys
from protocol import api_pb2 as API
from protocol import api_pb2_grpc as API_gRPC
from protocol import data_pb2 as Data
from protocol import slam_pb2 as SLAM

class SLAMProcess():
    process = None
    def __init__(self):
        self.process = subprocess.Popen(
            ['./build/main',
             'ORB_SLAM2/Vocabulary/ORBvoc.txt', 'slam/TUM.yaml'],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=sys.stderr)

        while True:
            r = self.process.stdout.readline()
            print(r)
            if r == b'INITIALIZED\n':
                break

    def send(self, request):
        # print('send:')
        data_bytes = request.SerializeToString()
        size = len(data_bytes)
        size_bytes = size.to_bytes(4, byteorder='little')
        # print(data_bytes, size, size_bytes)
        self.process.stdin.write(size_bytes)
        self.process.stdin.write(data_bytes)
        self.process.stdin.flush()

    def receive(self):
        size_bytes = self.process.stdout.read(4)
        size = int.from_bytes(size_bytes, 'little')
        data_bytes = self.process.stdout.read(size)

        # print('return:')
        # print(data_bytes)
        result = SLAM.TrackResult()
        result.ParseFromString(data_bytes)
        return result




class APIServicer(API_gRPC.APIServicer):

    slam_pool = []

    SLAM_POOL_SIZE = 1

    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

        for _ in range(self.SLAM_POOL_SIZE):
            loop.run_in_executor(None, self.add_slam_pool)


    def add_slam_pool(self):
        self.slam_pool += [SLAMProcess()]

    def get_slam_from_pool(self):
        if not self.slam_pool:
            return SLAMProcess()

        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(None, self.add_slam_pool)
        return self.slam_pool.pop()

    def GetInfo(self, request, context):
        return API.Info(version='0.1.0')

    def Track(self, request_iterator, context):

        try:

            print('track init\n')

            print(request_iterator.__next__())

            slam = self.get_slam_from_pool()

            frame = Data.JPEGFrame(data=b'')
            print(frame)

            request = SLAM.TrackRequest(id=1, frame=frame)

            print(request)

            slam.send(request)

            print(slam.receive())

            yield(API.Update())

        except Exception as err:
            print(err)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    API_gRPC.add_APIServicer_to_server(APIServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    print("Starting server...\n")

    serve()
