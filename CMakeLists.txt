cmake_minimum_required(VERSION 3.20)
project(MagneticAdventureCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  add_compile_options(/W3 /MP /EHsc)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
endif()

# ---- vendored Box2D 2.0.1 (见 docs/facts.md F14；原 b2Physics.dll 静态链接 2.0.x) ----
set(B2_ROOT ${CMAKE_SOURCE_DIR}/vendor/box2d-2.0.1/Box2D)
file(GLOB_RECURSE B2_SOURCES CONFIGURE_DEPENDS ${B2_ROOT}/Source/*.cpp)
add_library(box2d STATIC ${B2_SOURCES})
target_include_directories(box2d PUBLIC
  ${B2_ROOT}/Include
  ${B2_ROOT}/Source
  ${B2_ROOT}/Source/Common
  ${B2_ROOT}/Source/Collision
  ${B2_ROOT}/Source/Collision/Shapes
  ${B2_ROOT}/Source/Dynamics
  ${B2_ROOT}/Source/Dynamics/Contacts
  ${B2_ROOT}/Source/Dynamics/Joints)
