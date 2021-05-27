cmake_minimum_required(VERSION 2.9)
project(slam)

set(CMAKE_MACOSX_RPATH OFF)

add_definitions(-std=c++11)

add_subdirectory(ORB_SLAM2)
add_subdirectory(protocol)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

find_package(OpenCV REQUIRED)

find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIR})

set(THREADS_PREFER_PTHREAD_FLAG ON)  
find_package(Threads REQUIRED)

include_directories(ORB_SLAM2 ORB_SLAM2/include ${OpenCV_INCLUDE_DIRS})

add_executable(main slam/main.cpp)
target_link_libraries(main ORB_SLAM2 ${OpenCV_LIBS} Threads::Threads protocol ${PROTOBUF_LIBRARY} "-pthread")
