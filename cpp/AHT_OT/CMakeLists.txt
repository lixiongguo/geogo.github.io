cmake_minimum_required(VERSION 3.16)
project(AHT_OT LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(EIGEN3_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../deps/eigen-3.4.0"
    CACHE PATH "Eigen include dir")
set(STB_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../deps/stb" CACHE PATH "stb include dir")

if(NOT TARGET Eigen3::Eigen)
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    set_target_properties(Eigen3::Eigen PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}")
endif()

add_library(aht_ot STATIC src/stb_impl.cpp)
target_include_directories(aht_ot PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${STB_DIR}
)
target_link_libraries(aht_ot PUBLIC Eigen3::Eigen)

if(MSVC)
    set(_aht_msvc_flags /Zc:__cplusplus /utf-8)
    target_compile_options(aht_ot PRIVATE ${_aht_msvc_flags})
else()
    target_compile_options(aht_ot PRIVATE -O3)
endif()

function(aht_ot_exe name src)
    add_executable(${name} ${src})
    target_link_libraries(${name} PRIVATE aht_ot)
    if(MSVC)
        target_compile_options(${name} PRIVATE ${_aht_msvc_flags})
    endif()
endfunction()

aht_ot_exe(run_aht_ot examples/run_aht_ot.cpp)
aht_ot_exe(transition_demo examples/transition_demo.cpp)
aht_ot_exe(run_tests examples/run_tests.cpp)
