cmake_minimum_required(VERSION 3.20)
project(MagneticAdventureCpp LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  add_compile_options(/W3 /MP /EHsc /utf-8)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
  # x87 而非 SSE2：原 b2Physics.dll 的浮点运算全部走 x87（InitVelocityConstraints 444 条指令
  # 里 359 条 fld/fmul/fadd…，零 SSE 标量），中间精度不同会让结果在第 1 步就差 1e-4。
  # 用 /arch:IA32 后 6 个关卡 53,000+ 步的 body 状态与原版**逐位一致**（F82）。
  add_compile_options(/arch:IA32)
endif()

# ---- vendored Box2D 2.0.2 ----
# 依据 docs/facts.md F27/F28：原 b2Physics.dll 的 b2Body/b2World 布局与该快照逐项一致
# （2.0.1 相差 16/4 字节，已排除）。唯一改动：b2_maxPolygonVertices 16 -> 8。
set(B2_ROOT ${CMAKE_SOURCE_DIR}/vendor/box2d-2.0.2/Box2D)
file(GLOB_RECURSE B2_SOURCES CONFIGURE_DEPENDS ${B2_ROOT}/*.cpp)
add_library(box2d STATIC ${B2_SOURCES})
set_target_properties(box2d PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
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
  src/b2physics/b2physics.def)
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
target_link_options(b2physics PRIVATE "/MAP")
set_target_properties(b2physics PROPERTIES OUTPUT_NAME b2Physics
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# ---- 转发 DLL（proxy）：占住 b2Physics.dll 文件名，加载 b2Physics_orig.dll，
#      记录每次导出的实参 + 指针内存，然后把调用原样尾跳给原 DLL。
#      依据：docs/facts.md F34/F38；生成器 tools/gen_proxy.py。
add_library(b2physics_proxy SHARED
  src/proxydll/proxy_core.c
  src/proxydll/proxy_stubs.c
  src/proxydll/proxy.def)
target_link_options(b2physics_proxy PRIVATE /MAP)
set_target_properties(b2physics_proxy PROPERTIES OUTPUT_NAME b2Physics
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/proxy"
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
