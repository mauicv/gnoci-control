cmake_minimum_required(VERSION 3.22)
project(gnoci LANGUAGES CXX)

include(FetchContent)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

FetchContent_Declare(MiniPID
  GIT_REPOSITORY https://github.com/tekdemo/MiniPID.git
  GIT_TAG        6ff76acc9562e75649c4532225183686ace901b3
)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
)

# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

FetchContent_MakeAvailable(MiniPID)
add_library(minipid STATIC
  ${minipid_SOURCE_DIR}/MiniPID.cpp
)
target_include_directories(minipid
  PUBLIC
    # Mark as SYSTEM to silence 3rd-party warnings
    $<BUILD_INTERFACE:${minipid_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>      # harmless if you don’t install
)

add_library(scheduled_executor INTERFACE)
target_include_directories(scheduled_executor INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)   

add_executable(gnoci src/main.cpp)

find_package(fmt CONFIG REQUIRED)
target_link_libraries(gnoci PRIVATE fmt::fmt)

# Find pigpiod_if2
find_library(PIGPIOD_IF2_LIB NAMES pigpiod_if2 REQUIRED)
target_link_libraries(gnoci PRIVATE ${PIGPIOD_IF2_LIB})

# Also need pthread for pigpio
find_package(Threads REQUIRED)
target_link_libraries(gnoci PRIVATE Threads::Threads)

# Find minipid
# find_package(minipid CONFIG REQUIRED)
target_link_libraries(gnoci PRIVATE minipid)

target_link_libraries(gnoci PRIVATE scheduled_executor)


enable_testing()

add_executable(
  all_tests
  tests/all_tests.cc
  tests/test_servo.cc
  tests/test_servo_group.cc
)
target_link_libraries(
  all_tests
  GTest::gtest_main
  minipid
)
include(GoogleTest)
gtest_discover_tests(all_tests)