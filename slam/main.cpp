#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>
#include<unistd.h>
#include<vector>
#include<thread>

#include<opencv2/opencv.hpp>

#include <include/System.h>

#include <google/protobuf/util/time_util.h>

#include "protocol/slam.pb.h"
#include "protocol/data.pb.h"

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cout << "Invalid arguments" << std::endl;
        return 1;
    }



    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);

    std::cout << "INITIALIZED" << std::endl;

    // std::thread runthread([&]() {
    //     std::cout << "<VIEWER STARTED>" << std::endl;
    //     SLAM.StartViewer();
    // });

    while (true) {
        slam::TrackRequest request;


        char size_buf[4];
        std::cin.read(size_buf, 4);

        unsigned input_size =
            (unsigned char)size_buf[0]
            | (unsigned char)size_buf[1] << 8
            | (unsigned char)size_buf[2] << 16
            | (unsigned char)size_buf[3] << 24;

        if (input_size > 1024 * 1024)
            std::cout << "BUFFER OVERFLOW: "  << input_size << std::endl;

        char input_buf[1024*1024];
        std::cin.read(input_buf, input_size);

        std::string input(input_buf, input_size);

        if (!request.ParseFromString(input)) {
            std::cout << "<Failed to parse request>" << std::endl;

            for (int i = 0; i < input_size; i++) {
                std::cout << '\\' << (unsigned)input[i];
            }
            std::cout << endl;
        }

        if (request.has_reset() && request.reset()) {
            std::cout << "<RESET SLAM>" << std::endl;

            SLAM.Reset();
            // SLAM.StartViewer();

            continue;
        }


        auto frame_data = request.frame().data();
        double timestamp =
            request.frame().timestamp().seconds() +
            request.frame().timestamp().nanos() * 1e-9;
        // std::cout << "<RECEIVED>" << setprecision(15) << timestamp
        //           <<  " " << frame_data.length() << std::endl;
        std::vector<uchar> png(frame_data.begin(), frame_data.end());
        cv::Mat frame = cv::imdecode(png, cv::IMREAD_COLOR);

        if (frame.empty()) std::cout << "<EMPTY IMAGE>" << std::endl;

        // cv::imwrite("img.png", frame);

        cv::Mat camera_pose = SLAM.TrackMonocular(frame, timestamp);


        std::cout << "<POSE>\n" << SLAM.GetTrackingState() << camera_pose << std::endl;
        std::cout << SLAM.GetTrackedMapPoints().size() << std::endl;


        const auto& origin = new Location();
        origin->set_latitude(1);
        origin->set_longitude(2);
        origin->set_height(3);

        const auto& camera = new Camera();
        camera->set_allocated_location(origin);

        const auto& result = new slam::TrackResult();
        result->set_allocated_camera(camera);

        std::string output;
        result->SerializeToString(&output);

        unsigned output_size = output.length();
        std::cout << '\0'
                  << ((char)output_size)
                  << ((char)(output_size >> 8))
                  << ((char)(output_size >> 16))
                  << ((char)(output_size >> 24));

        std::cout << output;
    }


    return 0;
}
