import time
import grpc
from protocol import api_pb2_grpc
from protocol import api_pb2


def track_request():
    yield api_pb2.Request(userId=42)
    time.sleep(10)

if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = api_pb2_grpc.APIStub(channel)

    for track_result in stub.Track(track_request()):
        print(track_result)

