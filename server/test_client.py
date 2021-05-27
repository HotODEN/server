import time
import datetime
import grpc
import glob
import io
from PIL import Image
from google.protobuf.timestamp_pb2 import Timestamp
from protocol import api_pb2 as API
from protocol import api_pb2_grpc as API_gRPC
from protocol import data_pb2 as Data

images = sorted(glob.glob('ORB_SLAM2/sequence/rgbd_dataset_freiburg1_xyz/rgb/*.png'))

def track_request():
    for path in images:
        # img = Image.open(path)
        # img_bytes = io.BytesIO()
        # img.save(img_bytes, format='PNG')
        # jpeg_data = img_bytes.getvalue()

        png_data = open(path, 'rb').read()

        t = datetime.datetime.now().timestamp()
        timestamp = Timestamp(seconds=int(t), nanos=int(t % 1 * 1e9))
        frame = Data.PNGFrame(timestamp=timestamp, data=png_data)

        print(path, frame.timestamp)

        yield API.Request(userId=42, frame=frame)

        time.sleep(0.03)

    print('end')

if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = API_gRPC.APIStub(channel)

    for track_result in stub.Track(track_request()):
        print(track_result)

