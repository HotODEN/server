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

images = sorted(glob.glob('ORB_SLAM2/sequence/freiburg1_xyz/rgb/*.png'))

def track_request():
    for path in images[:]:
        png_data = open(path, 'rb').read()

        t = datetime.datetime.now().timestamp()
        timestamp = Timestamp(seconds=int(t), nanos=int(t % 1 * 1e9))
        frame = Data.PNGFrame(timestamp=timestamp, data=png_data)

        print(path)

        yield API.Request(userId=42, frame=frame)

        time.sleep(0.1)

    print('end')

if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = API_gRPC.APIStub(channel)


    cloud = o3d.geometry.PointCloud()


    points = np.asarray([[0, 0, 0], [0, 1, 0]])
    colors = np.asarray([[0, 0, 0], [0, 1, 0]])
    cloud.points = o3d.utility.Vector3dVector(points)
    cloud.colors = o3d.utility.Vector3dVector(colors)


    # o3d.visualization.draw_geometries([cloud])

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(cloud)
    vis.get_render_option().point_size = 20

    def updating_thread():
        for update in stub.Track(track_request()):
            cloud.points.clear()
            cloud.colors.clear()
            # points = np.zeros((len(update.points), 3))
            # colors = np.zeros((len(update.points), 3))

            for i, point in enumerate(update.points):
                # points[i][0] = point.pos.x
                # points[i][1] = point.pos.y
                # points[i][2] = point.pos.z

                # colors[i][0] = point.color.red
                # colors[i][1] = point.color.green
                # colors[i][2] = point.color.blue


                cloud.points.append(
                    [point.pos.x, point.pos.y, point.pos.z])
                cloud.colors.append(
                    [point.color.red, point.color.green, point.color.blue])

                # if i == 0:
                #     print(point)

            print(len(update.points), update.state)

            # cloud.points.append(points)
            # cloud.colors.append(colors)


    thread = threading.Thread(target=updating_thread)
    thread.start()

    while True:
        time.sleep(0.03)
        vis.update_geometry(cloud)
        vis.poll_events()
        vis.update_renderer()

    thread.join()

    vis.destroy_window()










