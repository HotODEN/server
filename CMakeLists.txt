cmake_minimum_required(VERSION 2.9)
project(slam)

set(CMAKE_MACOSX_RPATH OFF)

add_definitions(-std=c++11)

add_subdirectory(ORB_SLAM2)
add_subdirectory(protocol)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIR})

include_directories(ORB_SLAM2 ORB_SLAM2/include)

add_executable(main slam/main.cpp)
target_link_libraries(main ORB_SLAM2 protocol ${PROTOBUF_LIBRARY})
