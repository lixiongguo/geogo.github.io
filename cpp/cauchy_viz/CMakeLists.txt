cmake_minimum_required(VERSION 3.16)
project(cauchy_viz LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(WIN32)
    set(THREADS_PREFER_PTHREAD_FLAG OFF CACHE BOOL "" FORCE)
endif()

include(FetchContent)

FetchContent_Declare(
    glfw
    GIT_REPOSITORY https://github.com/glfw/glfw.git
    GIT_TAG 3.4
    GIT_SHALLOW TRUE
)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(glfw)

FetchContent_Declare(
    glad
    GIT_REPOSITORY https://github.com/Dav1dde/glad.git
    GIT_TAG v2.0.8
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(glad)
include(${glad_SOURCE_DIR}/cmake/GladConfig.cmake)
glad_add_library(glad_gl33 REPRODUCIBLE LOADER API gl:core=3.3)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../p2p_harmonic
                 ${CMAKE_BINARY_DIR}/p2p_harmonic)

add_executable(cauchy_viz
    main.cpp
    CauchyScene.cpp
    DataLoader.cpp
    Renderer.cpp
)

target_compile_definitions(cauchy_viz PRIVATE GLFW_INCLUDE_NONE)

target_include_directories(cauchy_viz PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/gladsources/glad_gl33/include
)

target_link_libraries(cauchy_viz PRIVATE
    p2p_harmonic
    glfw
    glad_gl33
)

if(WIN32)
    target_link_libraries(cauchy_viz PRIVATE opengl32)
elseif(APPLE)
    target_link_libraries(cauchy_viz PRIVATE "-framework OpenGL")
else()
    target_link_libraries(cauchy_viz PRIVATE GL)
endif()

add_custom_command(TARGET cauchy_viz POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:cauchy_viz>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../cauchy_viz$<IF:$<PLATFORM_ID:Windows>,.exe,>
)
