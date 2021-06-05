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

        print(path)

        yield API.Request(userId=42, frame=frame)

        time.sleep(0.1)

    print('end')

if __name__ == "__main__":
    print ("Starting client...")

    channel = grpc.insecure_channel('localhost:8080')
    stub = API_gRPC.APIStub(channel)


    cloud = o3d.geometry.PointCloud()


    points = np.asarray([[0, 0, 0], [0, 1, 0], [1, 0, 0]])
    normals = np.asarray([[0, 0, 1], [0, 1, 0], [0, 0, 0]])
    colors = np.asarray([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    triangles = np.asarray([[0, 1, 2]])
    cloud.points = o3d.utility.Vector3dVector(points)
    cloud.normals = o3d.utility.Vector3dVector(normals)
    cloud.colors = o3d.utility.Vector3dVector(colors)

    mesh = o3d.geometry.TriangleMesh.create_sphere()
    mesh.compute_vertex_normals()

    # mesh.vertices = o3d.utility.Vector3dVector(points)
    # mesh.triangles = o3d.utility.Vector3iVector(triangles)

    # o3d.visualization.draw_geometries([cloud])

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(cloud)
    # vis.add_geometry(mesh)
    vis.get_render_option().point_size = 20

    def updating_thread():
        for update in stub.Track(track_request()):
            cloud.points.clear()
            cloud.normals.clear()
            cloud.colors.clear()
            # points = np.zeros((len(update.points), 3))
            # colors = np.zeros((len(update.points), 3))

            vertices = np.empty((len(update.mesh.vertices), 3),
                                dtype=np.float64)
            colors = np.empty((len(update.mesh.vertices), 3),
                                dtype=np.float64)
            for i, point in enumerate(update.mesh.vertices):
                vertices[i][0] = point.position.x
                vertices[i][1] = point.position.y
                vertices[i][2] = point.position.z
                colors[i][0] = point.color.red
                colors[i][1] = point.color.green
                colors[i][2] = point.color.blue

            triangles = np.empty((len(update.mesh.triangles)*2, 3),
                                 dtype=np.int32)
            for i, triangle in enumerate(update.mesh.triangles):
                triangles[i*2][0] = triangle.a
                triangles[i*2][1] = triangle.b
                triangles[i*2][2] = triangle.c
                triangles[i*2+1][0] = triangle.a
                triangles[i*2+1][1] = triangle.c
                triangles[i*2+1][2] = triangle.b



            if vertices.size > 0 and triangles.size > 0:
                mesh.vertices = o3d.utility.Vector3dVector(vertices)
                mesh.vertex_colors = o3d.utility.Vector3dVector(colors)
                mesh.triangles = o3d.utility.Vector3iVector(triangles)
                # mesh.compute_vertex_normals()

                # o3d.visualization.draw_geometries([mesh])

            for i, point in enumerate(update.mesh.vertices):
                # points[i][0] = point.position.x
                # points[i][1] = point.position.y
                # points[i][2] = point.position.z

                # colors[i][0] = point.color.red
                # colors[i][1] = point.color.green
                # colors[i][2] = point.color.blue


                cloud.points.append(
                    [point.position.x, point.position.y, point.position.z])
                cloud.normals.append(
                    [point.normal.x, point.normal.y, point.normal.z])
                cloud.colors.append(
                    [point.color.red, point.color.green, point.color.blue])

                # if i == 0:
                #     print(point)

            print(len(update.mesh.vertices),
                  len(update.mesh.triangles),
                  update.state)



            # cloud.points.append(points)
            # cloud.colors.append(colors)

    # updating_thread()


    thread = threading.Thread(target=updating_thread)
    thread.start()

    while True:
        time.sleep(0.03)
        vis.update_geometry(cloud)
        vis.update_geometry(mesh)
        vis.poll_events()
        vis.update_renderer()

    thread.join()

    vis.destroy_window()










