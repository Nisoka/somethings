cmake_minimum_required(VERSION 3.2)
project(cc)

enable_language(CXX)

# add definitions macro
# add_definitions(-std=c++11)
# ADD_DEFINITIONS(-fpermissive)

# set release model
SET(CMAKE_BUILD_TYPE "Release")
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall -std=c++11")
# SET(CMAKE_CXX_COMPILER /usr/bin/g++)     

# set debug model
# SET(CMAKE_BUILD_TYPE "Debug")
# SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g -std=c++11")
# # SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g2 -ggdb --std=c++11")

include_directories(include)

add_subdirectory(base)
