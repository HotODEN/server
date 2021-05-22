import grpc
from protocol import api_pb2_grpc
from protocol import api_pb2


if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = api_pb2_grpc.APIStub(channel)

    print(stub.GetInfo(api_pb2.Client()))
