cmake_minimum_required(VERSION 2.9)
project(slam)

add_definitions(-std=c++11)

add_subdirectory(ORB_SLAM2)
add_subdirectory(protocol)

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_BINARY_DIR})


FIND_PACKAGE(Protobuf REQUIRED)
message(STATUS "Protobuf: "${PROTOBUF_INCLUDE_DIR})
INCLUDE_DIRECTORIES(${PROTOBUF_INCLUDE_DIR})

ADD_EXECUTABLE(main slam/main.cpp)
TARGET_LINK_LIBRARIES(main protocol ${PROTOBUF_LIBRARY})
