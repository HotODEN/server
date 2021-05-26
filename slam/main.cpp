#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>
#include<unistd.h>

// #include<opencv2/core/core.hpp>

#include <include/System.h>

#include "protocol/slam.pb.h"
#include "protocol/data.pb.h"

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "Invalid arguments" << std::endl;
        return 1;
    }

    // ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);

    std::cout << "INITIALIZED" << std::endl;


    std::cerr << "<STDERR>" << std::endl;



    while (true) {
        slam::TrackRequest request;


        char size_buf[4];
        std::cin.read(size_buf, 4);

        unsigned input_size =
            (unsigned)size_buf[3] << 24 |
            (unsigned)size_buf[2] << 16 |
            (unsigned)size_buf[1] << 8 |
            (unsigned)size_buf[0];

        if (input_size > 1024 * 1024)
            std::cerr << "BUUFFER OVERFLOW: "  << input_size << std::endl;

        char input_buf[1024*1024];
        std::cin.read(input_buf, input_size);

        std::string input(input_buf, input_size);

        if (!request.ParseFromString(input)) {
            std::cerr << "<Failed to parse request>" << std::endl;

            for (int i = 0; i < input_size; i++) {
                std::cerr << '\\' << (unsigned)input[i];
            }
            std::cerr << endl;
        }


        // std::cerr << "<RECEIVED>" << request.id() << std::endl;

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
        std::cout << ((char)output_size);
        std::cout << ((char)(output_size >> 8));
        std::cout << ((char)(output_size >> 16));
        std::cout << ((char)(output_size >> 24));

        std::cout << output;
    }

    return 0;
}
