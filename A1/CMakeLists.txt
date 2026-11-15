cmake_minimum_required(VERSION 3.16)
project(CppThreeJsControl LANGUAGES CXX)

if(POLICY CMP0167)
    cmake_policy(SET CMP0167 NEW)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#µÚÈý·½¿â 
find_package(Boost 1.70 REQUIRED)
find_package(Threads REQUIRED)

add_executable(relay_server src/relay_server.cpp)
add_executable(controller src/controller.cpp)

foreach(target IN ITEMS relay_server controller)
    target_include_directories(${target} PRIVATE ${Boost_INCLUDE_DIRS})
    target_compile_definitions(${target} PRIVATE BOOST_ERROR_CODE_HEADER_ONLY)
    target_link_libraries(${target} PRIVATE Threads::Threads)
    if(WIN32)
        target_link_libraries(${target} PRIVATE ws2_32 mswsock)
        target_compile_options(${target} PRIVATE /utf-8)
    endif()
endforeach()
