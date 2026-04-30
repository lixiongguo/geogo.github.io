cmake_minimum_required(VERSION 3.10)
project(BoundedDistortion)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Eigen3
find_package(Eigen3 REQUIRED)

# Option: use libigl for I/O (set -DHAS_LIBIGL=ON)
option(HAS_LIBIGL "Use libigl for mesh I/O" OFF)

add_executable(bounded_distortion bounded_distortion_example.cpp)

target_include_directories(bounded_distortion PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${EIGEN3_INCLUDE_DIR}
)

if(HAS_LIBIGL)
    find_package(libigl REQUIRED)
    target_link_libraries(bounded_distortion igl::core)
    target_compile_definitions(bounded_distortion PRIVATE HAS_LIBIGL)
endif()

# Optimization flags
if(MSVC)
    target_compile_options(bounded_distortion PRIVATE /O2 /arch:AVX2)
else()
    target_compile_options(bounded_distortion PRIVATE -O3 -march=native)
endif()
