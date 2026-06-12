# MongeAmpere++ — CGAL optimal transport + Geogram Power diagram (WASM)
# Created from upstream cgal_create_cmake_script; extended for ma_power_diagram.

project(MA)

cmake_minimum_required(VERSION 3.16)
set(CMAKE_CXX_STANDARD 14)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "RELWITHDEBINFO")
endif()

add_definitions(-std=c++11 -g)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

find_package(CImg REQUIRED)
include_directories(${CIMG_INCLUDE_DIRS})
link_libraries(${CIMG_PROCESS_LIBS})

find_package(SuiteSparse)
include_directories(${SUITESPARSE_INCLUDE_DIRS})
link_libraries(${SUITESPARSE_LIBRARIES})

if(SUITESPARSEQR_FOUND)
  add_definitions(-DMA_USE_SUITESPARSE_QR)
endif()

set(Boost_USE_STATIC_LIBS ON)
find_package(Boost COMPONENTS timer chrono REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
link_libraries(${Boost_LIBRARIES})

find_package(CGAL REQUIRED)

# Avoid Anaconda X11 on macOS; on Windows CGAL apps may still need X11 for CImg display.
if(WIN32)
  set(CMAKE_INCLUDE_PATH "${CMAKE_INCLUDE_PATH}")
else()
  set(CMAKE_INCLUDE_PATH "/opt/X11/include;${CMAKE_INCLUDE_PATH}")
  find_package(X11 REQUIRED)
  include_directories(${X11_INCLUDE_DIR})
  link_libraries(${X11_LIB})
endif()

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# --- Geogram Power diagram (no CGAL); linked by build_wasm_power_diagram.ps1 ---
add_library(ma_power_diagram STATIC src/ma_power_diagram.cpp)
target_include_directories(ma_power_diagram PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

if(NOT CGAL_FOUND)
  message(STATUS "CGAL not found: CGAL tests disabled; ma_power_diagram may still build with Geogram.")
else()
  include(${CGAL_USE_FILE})
  find_package(Boost REQUIRED)
  if(NOT Boost_FOUND)
    message(STATUS "Boost not found: CGAL tests disabled.")
  else()
    include(CGAL_CreateSingleSourceCGALProgram)
    add_subdirectory(tests)
  endif()
endif()

# Optional native test for Geogram power diagram (not CGAL).
option(MA_BUILD_POWER_DIAGRAM_TEST "Build test_power_diagram (needs Geogram)" OFF)
if(MA_BUILD_POWER_DIAGRAM_TEST)
  if(NOT GEOGRAM_INSTALL_PREFIX)
    message(WARNING "Set -DGEOGRAM_INSTALL_PREFIX=... to link test_power_diagram")
  else()
    target_include_directories(ma_power_diagram PUBLIC
      ${GEOGRAM_INSTALL_PREFIX}/include/geogram1)
    find_library(GEOGRAM_LIB geogram PATHS ${GEOGRAM_INSTALL_PREFIX}/lib NO_DEFAULT_PATH)
    if(GEOGRAM_LIB)
      target_link_libraries(ma_power_diagram PUBLIC ${GEOGRAM_LIB})
      add_executable(test_power_diagram tests/test_power_diagram.cpp)
      target_link_libraries(test_power_diagram PRIVATE ma_power_diagram)
    endif()
  endif()
endif()
