if(NOT TARGET Eigen3::Eigen)
  add_library(Eigen3::Eigen INTERFACE IMPORTED)
  set_target_properties(Eigen3::Eigen PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/cpp/deps/eigen-3.4.0"
  )
endif()
