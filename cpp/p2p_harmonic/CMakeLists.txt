cmake_minimum_required(VERSION 3.16)
project(p2p_harmonic_prep LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
    Eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG 3.4.0
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(Eigen)

add_library(p2p_harmonic STATIC
    GeomUtils.cpp
    CauchyCoordinates.cpp
    P2PHarmonicPrep.cpp
)

target_include_directories(p2p_harmonic PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(p2p_harmonic PUBLIC Eigen3::Eigen)

add_executable(test_p2p_harmonic_prep test_p2p_harmonic_prep.cpp)
target_link_libraries(test_p2p_harmonic_prep PRIVATE p2p_harmonic)
