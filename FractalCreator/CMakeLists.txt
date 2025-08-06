cmake_minimum_required(VERSION 3.15)
project(FractalMutator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# SFML 3 con vcpkg
find_package(SFML 3 REQUIRED COMPONENTS Graphics Window System)

add_executable(FractalMutator src/gui/FractalMutator.cpp)

target_link_libraries(FractalMutator PRIVATE SFML::Graphics SFML::Window SFML::System)
