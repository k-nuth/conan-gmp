cmake_minimum_required(VERSION 3.15)
project(crosscheck LANGUAGES C)

find_package(gmp REQUIRED CONFIG)

add_executable(crosscheck crosscheck.c)
target_link_libraries(crosscheck PRIVATE gmp::libgmp)
