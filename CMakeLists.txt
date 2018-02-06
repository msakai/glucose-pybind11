cmake_minimum_required(VERSION 3.7)

add_subdirectory(glucose)

set(PYBIND11_CPP_STANDARD -std=c++14)
add_subdirectory(pybind11)
pybind11_add_module(pyglucose SHARED pyglucose.cpp)
target_include_directories(pyglucose PUBLIC glucose)
target_link_libraries(pyglucose PRIVATE glucose)
