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

bool receive(slam::TrackRequest& request) {
    char size_buf[4];
    std::cin.read(size_buf, 4);

    unsigned input_size =
        (unsigned char)size_buf[0]
        | (unsigned char)size_buf[1] << 8
        | (unsigned char)size_buf[2] << 16
        | (unsigned char)size_buf[3] << 24;

    if (input_size > 1024 * 1024) {
        std::cerr << "BUFFER OVERFLOW: "  << input_size << std::endl;
        return false;
    }

    char input_buf[1024*1024];
    std::cin.read(input_buf, input_size);

    std::string input(input_buf, input_size);

    if (!request.ParseFromString(input)) {
        std::cerr << "<Failed to parse request>" << std::endl;

        for (int i = 0; i < input_size; i++) {
            std::cout << '\\' << (unsigned)input[i];
        }
        std::cout << endl;
        return false;
    }

    return true;
}

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

    // std::set<ORB_SLAM2::MapPoint*> trackedMapPoints;

    cv::Mat K = cv::Mat::eye(3,3,CV_32F);
    K.at<float>(0,0) = 517.306408;
    K.at<float>(1,1) = 516.469215;
    K.at<float>(0,2) = 318.643040;
    K.at<float>(1,2) = 255.313989;

    std::map<ORB_SLAM2::MapPoint*, cv::Vec3b> knownColors;

    while (true) {
        slam::TrackRequest request;

        if (!receive(request)) continue;

        if (request.has_reset() && request.reset()) {
            std::cerr << "<RESET SLAM>" << std::endl;
            SLAM.Reset();
            continue;
        }

        auto frame_data = request.frame().data();

        double timestamp = std::time(nullptr);

        std::vector<uchar> png(frame_data.begin(), frame_data.end());
        cv::Mat frame = cv::imdecode(png, cv::IMREAD_COLOR);

        if (frame.empty())  {
            std::cerr << "<EMPTY IMAGE>" << std::endl;
            continue;
        }


        cv::Mat Tcw = SLAM.TrackMonocular(frame, timestamp);

        // std::cerr << Tcw << std::endl;

        const auto& origin = new Location();
        origin->set_latitude(1);
        origin->set_longitude(2);
        origin->set_height(3);

        const auto& camera = new Camera();
        camera->set_allocated_location(origin);

        const auto& result = new slam::TrackResult();
        result->set_allocated_camera(camera);
        result->set_state(static_cast<TrackingState>(SLAM.GetTrackingState()));

        std::vector<ORB_SLAM2::MapPoint*> mapPoints =
            SLAM.GetAllMapPoints();

        // std::set<ORB_SLAM2::MapPoint*>
        //     refPoints(_refPoints.begin(), _refPoints.end());

        // std::vector<ORB_SLAM2::MapPoint*> trackedMapPoints;
        int size = 0;

        std::vector<ORB_SLAM2::MapPoint*> trackedMPs =
            SLAM.GetTrackedMapPoints();


        if (!Tcw.empty()) {
            bool show = true;

            cv::Mat ARt = K * Tcw.rowRange(0,3);

            for (int i = 0, end = trackedMPs.size(); i < end; i++) {
                ORB_SLAM2::MapPoint* mapPoint = trackedMPs[i];

                if (!mapPoint|| mapPoint->isBad()) continue;

                cv::Mat pos = mapPoint->GetWorldPos();

                // cv::Mat Rwc(3,3,CV_32F);
                // cv::Mat twc(3,1,CV_32F);

                // Rwc = Tcw.rowRange(0,3).colRange(0,3).t();
                // twc = -Rwc*Tcw.rowRange(0,3).col(3);


                // cv::Mat Rt;

                // cv::hconcat(Rwc, twc, Rt);

                cv::Mat pos_ = (cv::Mat_<float>(4, 1) <<
                                pos.at<float>(0),
                                pos.at<float>(1),
                                pos.at<float>(2),1);

                cv::Mat uv = ARt * pos_;

                int u = uv.at<float>(0) / uv.at<float>(2);
                int v = uv.at<float>(1) / uv.at<float>(2);


                if (0 <= u && u <= 640 && 0 <= v && v <= 480) {

                    // cv::Mat pos_in_image = Tcw * pos_;
                    // std::cerr << pos_in_image << std::endl;
                    // std::cerr << K << std::endl;
                    // std::cerr << Tcw << std::endl;
                    // std::cerr << pos_ << std::endl;
                    // std::cerr << Rwc << std::endl;
                    // std::cerr << twc << std::endl;
                    // std::cerr << Rt << std::endl;
                    // std::cerr << K * Rt * pos_ << std::endl;

                    cv::Vec3b pixel = frame.at<cv::Vec3b>(v, u);

                    if (knownColors.find(mapPoint) == knownColors.end()) {
                        knownColors[mapPoint] = pixel;
                    }
                    else {
                        knownColors[mapPoint] /= 2;
                        knownColors[mapPoint] += pixel / 2;
                    }

                    // Point* point = result->add_points();
                    // point->mutable_pos()->set_x(pos.at<float>(0));
                    // point->mutable_pos()->set_y(pos.at<float>(1));
                    // point->mutable_pos()->set_z(pos.at<float>(2));
                    // point->mutable_color()->set_blue(pixel[0] / 256.0);
                    // point->mutable_color()->set_green(pixel[1] / 256.0);
                    // point->mutable_color()->set_red(pixel[2] / 256.0);


                    // if (show) {
                    //     std::cerr << u << ' ' <<  v << std::endl;
                    //     std::cerr << pixel << std::endl;
                    //     std::cerr << point << std::endl;
                    //     show = false;
                    // }


                }


            }
        }

        for (int i = 0, end = mapPoints.size(); i < end; i++) {
            ORB_SLAM2::MapPoint* mapPoint = mapPoints[i];
            if (!mapPoint || mapPoint->isBad()) continue;

            cv::Mat pos = mapPoint->GetWorldPos();

            Point* point = result->add_points();
            point->mutable_pos()->set_x(pos.at<float>(0));
            point->mutable_pos()->set_y(-pos.at<float>(1));
            point->mutable_pos()->set_z(-pos.at<float>(2));

            if (knownColors.find(mapPoint) != knownColors.end()) {
                cv::Vec3b pixel = knownColors.at(mapPoint);

                point->mutable_color()->set_blue(pixel[0] / 256.0);
                point->mutable_color()->set_green(pixel[1] / 256.0);
                point->mutable_color()->set_red(pixel[2] / 256.0);
            }

            size++;
        }




        std::cerr << "SIZE: " << size << "/" << mapPoints.size()
                  << " " << SLAM.GetTrackingState()
                  << std::endl;



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
