cmake_minimum_required(VERSION 3.20)
project(polyscope-vector-field LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Polyscope (FetchContent) ──────────────────────────
include(FetchContent)
FetchContent_Declare(
    polyscope
    GIT_REPOSITORY https://github.com/nmwsharp/polyscope.git
    GIT_TAG        v2.6.1
)
FetchContent_MakeAvailable(polyscope)

# ── Eigen (local deps) ────────────────────────────────
set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../deps/eigen-3.4.0")
if(NOT EXISTS "${EIGEN3_INCLUDE_DIR}/Eigen/Core")
    message(FATAL_ERROR "Eigen not found at ${EIGEN3_INCLUDE_DIR}")
endif()

# ── Demo executable ───────────────────────────────────
add_executable(vector_field_demo main.cpp)
target_include_directories(vector_field_demo PRIVATE ${EIGEN3_INCLUDE_DIR})
target_link_libraries(vector_field_demo PRIVATE polyscope)
