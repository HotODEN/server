import asyncio
from concurrent import futures
import subprocess
import grpc
import sys
import open3d as o3d
from protocol import api_pb2 as API
from protocol import api_pb2_grpc as API_gRPC
from protocol import data_pb2 as Data
from protocol import slam_pb2 as SLAM

class SLAMProcess():
    process = None
    def __init__(self):
        self.process = subprocess.Popen(
            ['./build/main',
             'ORB_SLAM2/Vocabulary/ORBvoc.bin', 'slam/TUM.yaml'],
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

        self.process.stdin.write(size_bytes)
        self.process.stdin.write(data_bytes)
        self.process.stdin.flush()

    def receive(self):
        while True:
            # self.process.stdout.flush()
            c = self.process.stdout.read(1)
            # print('char: ', c)
            if c == b'':
                print('something wrong')
                break
            if c == b'\0':
                break
            r = self.process.stdout.readline()
            print(' ' + (c + r).decode('utf-8'))
            # self.process.stdout.flush()


        size_bytes = self.process.stdout.read(4)
        size = int.from_bytes(size_bytes, 'little')

        # print('size: ', size)

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

    def return_slam_to_pool(self, slam):
        self.slam_pool += [slam]

    def GetInfo(self, request, context):
        return API.Info(version='0.1.0')

    def Track(self, request_iterator, context):

        try:
            print('track init')

            slam = self.get_slam_from_pool()

            for req in request_iterator:

                frame = req.frame
                # print(frame)

                request = SLAM.TrackRequest(frame=frame)
                # print(request)

                slam.send(request)

                result = slam.receive()

                if not result.points:
                    yield(API.Update(state=result.state))
                    continue

                cloud = o3d.geometry.PointCloud()
                cloud.points = o3d.utility.Vector3dVector([])
                cloud.normals = o3d.utility.Vector3dVector([])
                cloud.colors = o3d.utility.Vector3dVector([])

                for point in result.points:
                    cloud.points.append([point.position.x,
                                         point.position.y,
                                         point.position.z])
                    cloud.normals.append([point.normal.x,
                                          point.normal.y,
                                          point.normal.z])
                    cloud.colors.append([point.color.red,
                                         point.color.green,
                                         point.color.blue])

                # cloud.estimate_normals()

                rec_mesh = (o3d.geometry.TriangleMesh
                            .create_from_point_cloud_alpha_shape(cloud, 0.1))

                # rec_mesh = (o3d.geometry.TriangleMesh
                #             .create_from_point_cloud_ball_pivoting(
                #                 cloud,
                #                 o3d.utility.DoubleVector(
                #                     [0.02, 0.04, 0.08, 0.16]))
                #             )

                mesh = Data.Mesh()
                for triangle in rec_mesh.triangles:
                    mesh.triangles.append(
                        Data.Triangle(a=triangle[0],
                                      b=triangle[1],
                                      c=triangle[2]))

                for i in range(len(rec_mesh.vertices)):
                    vertice = rec_mesh.vertices[i]
                    normal = rec_mesh.vertex_normals[i]
                    color = rec_mesh.vertex_colors[i]
                    pos = Data.Vec3(x=vertice[0], y=vertice[1], z=vertice[2])
                    norm = Data.Vec3(x=normal[0], y=normal[1], z=normal[2])
                    col = Data.Color(red=color[0],
                                     green=color[1],
                                     blue=color[2])
                    mesh.vertices.append(
                        Data.Point(position=pos, normal=norm, color=col))

                print(len(rec_mesh.vertices), len(result.points))

                yield(API.Update(state=result.state, mesh=mesh))

            print('end')

            request = SLAM.TrackRequest(reset=True)
            slam.send(request)
            self.return_slam_to_pool(slam)

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
