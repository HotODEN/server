import time
import datetime
import threading
import grpc
import glob
import io
import numpy as np
import open3d as o3d
from google.protobuf.timestamp_pb2 import Timestamp
from protocol import api_pb2 as API
from protocol import api_pb2_grpc as API_gRPC
from protocol import data_pb2 as Data

images = sorted(glob.glob('ORB_SLAM2/sequence/freiburg1_floor/rgb/*.png'))

def track_request():
    for path in images[:]:
        png_data = open(path, 'rb').read()

        t = datetime.datetime.now().timestamp()
        timestamp = Timestamp(seconds=int(t), nanos=int(t % 1 * 1e9))
        frame = Data.PNGFrame(timestamp=timestamp, data=png_data)

        print(path, frame.timestamp)

        yield API.Request(userId=42, frame=frame)

        time.sleep(0.1)

    print('end')

if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = API_gRPC.APIStub(channel)


    cloud = o3d.geometry.PointCloud()


    points = np.asarray([[0, 0, 0], [0, 1, 0]])
    cloud.points = o3d.utility.Vector3dVector(points)

    # o3d.visualization.draw_geometries([cloud])

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(cloud)

    def updating_thread():
        for update in stub.Track(track_request()):
            points = np.zeros((len(update.points), 3))
            for i, point in enumerate(update.points):
                points[i][0] = point.x
                points[i][1] = point.y
                points[i][2] = point.z

            print(len(points), update.state)

            cloud.points = o3d.utility.Vector3dVector(points)


    thread = threading.Thread(target=updating_thread)
    thread.start()

    while True:
        time.sleep(0.03)
        vis.update_geometry(cloud)
        vis.poll_events()
        vis.update_renderer()

    thread.join()

    vis.destroy_window()










