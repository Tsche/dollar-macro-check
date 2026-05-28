cmake_minimum_required(VERSION 3.20)
project(dollar_macros CXX C)

if(NOT LLVM_SRC_DIR)
  message(FATAL_ERROR "LLVM_SRC_DIR not specified. Use: -DLLVM_SRC_DIR=/path/to/llvm-project")
endif()

if(NOT EXISTS "${LLVM_SRC_DIR}/llvm/CMakeLists.txt")
  message(FATAL_ERROR "Invalid LLVM_SRC_DIR: ${LLVM_SRC_DIR}")
endif()

if(NOT LLVM_BUILD_DIR)
  set(LLVM_BUILD_DIR "${LLVM_SRC_DIR}/build")
endif()

if(NOT EXISTS "${LLVM_BUILD_DIR}/lib/cmake/llvm")
  message(FATAL_ERROR "LLVM not built at ${LLVM_BUILD_DIR}")
endif()

set(LLVM_DIR "${LLVM_BUILD_DIR}/lib/cmake/llvm" CACHE PATH "LLVM CMake directory" FORCE)
set(Clang_DIR "${LLVM_BUILD_DIR}/lib/cmake/clang" CACHE PATH "Clang CMake directory" FORCE)

find_package(LLVM REQUIRED CONFIG)
find_package(Clang REQUIRED CONFIG)

list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")
include(AddLLVM)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(
  ${LLVM_INCLUDE_DIRS}
  ${CLANG_INCLUDE_DIRS}
  ${LLVM_SRC_DIR}/llvm/include
  ${LLVM_SRC_DIR}/clang/include
  ${LLVM_SRC_DIR}/clang-tools-extra/clang-tidy
  ${LLVM_BUILD_DIR}/tools/clang-tools-extra/clang-tidy
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

add_definitions(${LLVM_DEFINITIONS})

add_library(dollar_macros SHARED
  src/dollar/DollarMacroCheck.cpp
  src/dollar/DollarTidyModule.cpp
)

target_compile_options(dollar_macros PRIVATE -fno-rtti)

if(APPLE)
  set(PLUGIN_EXT ".dylib")
elseif(WIN32)
  set(PLUGIN_EXT ".dll")
else()
  set(PLUGIN_EXT ".so")
endif()

set_target_properties(dollar_macros PROPERTIES
  CXX_STANDARD ${CMAKE_CXX_STANDARD}
  CXX_STANDARD_REQUIRED ON
  SUFFIX "${PLUGIN_EXT}"
  PREFIX ""
)

install(TARGETS dollar_macros LIBRARY DESTINATION lib RUNTIME DESTINATION bin)


