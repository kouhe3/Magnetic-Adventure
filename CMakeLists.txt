cmake_minimum_required(VERSION 3.20)
project(MagneticAdventureCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  add_compile_options(/W3 /MP /EHsc /utf-8)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
endif()

# ---- vendored Box2D 2.0.2 ----
# 依据 docs/facts.md F27/F28：原 b2Physics.dll 的 b2Body/b2World 布局与该快照逐项一致
# （2.0.1 相差 16/4 字节，已排除）。唯一改动：b2_maxPolygonVertices 16 -> 8。
set(B2_ROOT ${CMAKE_SOURCE_DIR}/vendor/box2d-2.0.2/Box2D)
file(GLOB_RECURSE B2_SOURCES CONFIGURE_DEPENDS ${B2_ROOT}/*.cpp)
add_library(box2d STATIC ${B2_SOURCES})
target_include_directories(box2d PUBLIC
  ${B2_ROOT}
  ${B2_ROOT}/Common
  ${B2_ROOT}/Collision
  ${B2_ROOT}/Collision/Shapes
  ${B2_ROOT}/Dynamics
  ${B2_ROOT}/Dynamics/Contacts
  ${B2_ROOT}/Dynamics/Joints
  ${B2_ROOT}/Dynamics/Controllers)

# ---- b2Physics 兼容 DLL（导出清单见 src/b2physics/*.def）----
add_library(b2physics SHARED
  src/b2physics/b2physics.cpp
  src/b2physics/b2physics-partial.def)
target_include_directories(b2physics PRIVATE
  src/b2physics
  ${B2_ROOT}
  ${B2_ROOT}/Common
  ${B2_ROOT}/Collision
  ${B2_ROOT}/Collision/Shapes
  ${B2_ROOT}/Dynamics
  ${B2_ROOT}/Dynamics/Contacts
  ${B2_ROOT}/Dynamics/Joints
  ${B2_ROOT}/Dynamics/Controllers)
target_link_libraries(b2physics PRIVATE box2d)
target_compile_definitions(b2physics PRIVATE B2PHYSICS_EXPORTS)
set_target_properties(b2physics PROPERTIES OUTPUT_NAME b2Physics)
