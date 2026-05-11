cmake_minimum_required(VERSION 3.10)
project(macro_demo)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Enable clang-tidy for this project
set(CMAKE_CXX_CLANG_TIDY "clang-tidy")

add_executable(demo src/main.cpp)
