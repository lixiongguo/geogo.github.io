cmake_minimum_required(VERSION 3.16)
project(OptimalMassTransport LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")

# Eigen 3.4.0
set(EIGEN3_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/../deps/eigen-3.4.0" CACHE PATH "Eigen include dir")
if(NOT TARGET Eigen3::Eigen)
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    set_target_properties(Eigen3::Eigen PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}"
    )
endif()

# stb_image
set(STB_DIR "${CMAKE_SOURCE_DIR}/../deps/stb")

add_executable(run_tests run_tests.cpp)
target_include_directories(run_tests PRIVATE
    ${EIGEN3_INCLUDE_DIR}
    ${STB_DIR}
    ${CMAKE_SOURCE_DIR}
)
target_link_libraries(run_tests Eigen3::Eigen)
