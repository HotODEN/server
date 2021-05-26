#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>
#include<unistd.h>

// #include<opencv2/core/core.hpp>

#include <include/System.h>

#include "protocol/slam.pb.h"

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "Invalid arguments" << std::endl;
        return 1;
    }

    ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);

    std::cout << "INITIALIZED" << std::endl;

    return 0;
}
