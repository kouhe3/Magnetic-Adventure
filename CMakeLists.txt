cmake_minimum_required(VERSION 3.20)
project(MagneticAdventureCpp LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  add_compile_options(/W3 /MP /EHsc /utf-8)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
endif()

# x87 而非 SSE2：原 b2Physics.dll 的浮点运算全部走 x87（InitVelocityConstraints 444 条指令
# 里 359 条 fld/fmul/fadd…，零 SSE 标量），中间精度不同会让结果在第 1 步就差 1e-4。
# 用 /arch:IA32 后已复跑的 12 关里 10 关容差内 0 差异（F82/F84）。
set(B2_ARCH "IA32" CACHE STRING "浮点架构（/arch:），原版全程 x87")
set(B2_FP "default" CACHE STRING "/fp: 模式；default=不显式指定（语义同 precise，F84）")
if(MSVC)
  add_compile_options(/arch:${B2_ARCH})
  if(NOT B2_FP STREQUAL "default")
    add_compile_options(/fp:${B2_FP})
  endif()
endif()

# ---- vendored Box2D 2.0.2 ----
# 依据 docs/facts.md F27/F28：原 b2Physics.dll 的 b2Body/b2World 布局与该快照逐项一致
# （2.0.1 相差 16/4 字节，已排除）。唯一改动：b2_maxPolygonVertices 16 -> 8。
set(B2_ROOT "${CMAKE_SOURCE_DIR}/vendor/box2d-2.0.2/Box2D" CACHE PATH "Box2D source root")
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

# ---- 构建指纹（F98）：门禁/sweep 的每行结论都要能回答「出自哪个构建」----
string(REPLACE ";" " " B2_RELEASE_FLAGS "${CMAKE_CXX_FLAGS_RELEASE}")
add_custom_command(TARGET b2physics POST_BUILD
  COMMAND ${CMAKE_COMMAND}
    -DOUT=${CMAKE_BINARY_DIR}/build_info.json
    -DDLL=$<TARGET_FILE:b2physics>
    -DLIB=$<TARGET_FILE:box2d>
    -DARCH=${B2_ARCH}
    -DFP=${B2_FP}
    -DMSVC=${MSVC_VERSION}
    -DTOOLSET=${MSVC_TOOLSET_VERSION}
    -DCXX=${CMAKE_CXX_COMPILER_VERSION}
    -DCONFIG=$<CONFIG>
    -DFLAGS=${B2_RELEASE_FLAGS}
    -P ${CMAKE_SOURCE_DIR}/cmake/build_info.cmake
  COMMENT "writing build/build_info.json (fingerprint)")

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

# ---- vendored Ogg Vorbis 解码（Squall 的唯一外部依赖）----
# 依据 docs/facts.md F133/F135：pak 内音频只有 35 个 .ogg，原 Squall.dll 把解码器静态链进去，
# 且不依赖任何外部 DLL。上游 vcproj 的 external/libogg、external/libvorbis 缺失，故直接编源码。
set(OGG_ROOT "${CMAKE_SOURCE_DIR}/vendor/libogg-1.3.5")
set(VORBIS_ROOT "${CMAKE_SOURCE_DIR}/vendor/libvorbis-1.3.7")
# 源列表照抄上游 lib/CMakeLists.txt（不含 vorbisenc.c 与 misc.c——后者是依赖 pthread 的调试分配器）
set(VORBIS_LIB_SOURCES
  mdct.c smallft.c block.c envelope.c window.c lsp.c lpc.c analysis.c synthesis.c
  psy.c info.c floor1.c floor0.c res0.c mapping0.c registry.c codebook.c
  sharedbook.c lookup.c bitrate.c vorbisfile.c)
list(TRANSFORM VORBIS_LIB_SOURCES PREPEND "${VORBIS_ROOT}/lib/")
add_library(squall_codec STATIC
  ${OGG_ROOT}/src/bitwise.c
  ${OGG_ROOT}/src/framing.c
  ${VORBIS_LIB_SOURCES})
set_target_properties(squall_codec PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
target_include_directories(squall_codec PUBLIC ${OGG_ROOT}/include ${VORBIS_ROOT}/include)

# ---- Squall 音频 DLL（上游 v1.48 源码，导出契约见 mapping/squall-exports.csv）----
# 依据 F131/F132：原 Squall.dll 与 xtreme3d/squall 的 99 个 DLL_API 名字逐一致；
# 宿主只静态导入 17 个。WMA 与 track 解码器上游已注释掉（SoundFile.cpp:139-197），不参与构建。
set(SQUALL_ROOT "${CMAKE_SOURCE_DIR}/vendor/squall/source")
file(GLOB SQUALL_SOURCES
  ${SQUALL_ROOT}/SoundEngine/*.cpp
  ${SQUALL_ROOT}/SoundEngine/ext/*.cpp
  ${SQUALL_ROOT}/SoundFile/*.cpp
  ${SQUALL_ROOT}/SoundFile/WAV/*.cpp
  ${SQUALL_ROOT}/SoundFile/MP3/*.cpp
  ${SQUALL_ROOT}/SoundFile/Ogg/*.cpp)
add_library(squall SHARED ${SQUALL_SOURCES})
target_include_directories(squall PRIVATE
  ${SQUALL_ROOT}
  ${SQUALL_ROOT}/SoundEngine
  ${SQUALL_ROOT}/SoundFile
  ${SQUALL_ROOT}/SoundFile/WAV
  ${SQUALL_ROOT}/SoundFile/MP3
  ${SQUALL_ROOT}/SoundFile/Ogg
  ${SQUALL_ROOT}/../external/dshow)
target_compile_definitions(squall PRIVATE _WINDOWS _USRDLL SQUALL_EXPORTS WIN32
  # 上游 SoundEngine/ext/dsound.h 是手写的精简头，缺 DSBUFFERDESC.guid3DAlgorithm；
  # 让它不再遮蔽 SDK 头（2006 年的原构建用的就是 DX SDK 全量头）。
  DIRECTSOUND_VERSION=0x0800)
target_link_libraries(squall PRIVATE squall_codec dsound dxguid winmm ole32 user32
  "${SQUALL_ROOT}/../external/dshow/amstrmid.lib")
set_target_properties(squall PROPERTIES OUTPUT_NAME Squall
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# ---- 转发 DLL（Squall）：占住 Squall.dll 文件名，加载 Squall_orig.dll，
#      记录每次导出的实参/返回值/出参内存。依据 F131/F136（契约要以原版调用序为准）。
#      桩由 tools/gen_proxy.py 生成：
#        python tools/gen_proxy.py --csv mapping/squall-exports.csv \
#          --out-c src/squallproxy/proxy_stubs.c --out-def src/squallproxy/proxy.def \
#          --library Squall --prefix SQUALL_
add_library(squall_proxy SHARED
  src/squallproxy/proxy_core.c
  src/squallproxy/proxy_stubs.c
  src/squallproxy/proxy.def)
set_target_properties(squall_proxy PROPERTIES OUTPUT_NAME Squall
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/proxy_squall"
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# ---- 诊断变体：SQUALL_DEBUG=1 时 api_Startup 会在进程 CWD 写 Squall.log，
#      每个导出记参数与结果。默认不编；cmake -DSQUALL_DEBUG_LOG=ON 打开。
option(SQUALL_DEBUG_LOG "构建带 SQUALL_DEBUG 日志的 Squall 变体" OFF)
if(SQUALL_DEBUG_LOG)
  add_library(squall_dbg SHARED ${SQUALL_SOURCES})
  target_include_directories(squall_dbg PRIVATE
    ${SQUALL_ROOT}
    ${SQUALL_ROOT}/SoundEngine
    ${SQUALL_ROOT}/SoundFile
    ${SQUALL_ROOT}/SoundFile/WAV
    ${SQUALL_ROOT}/SoundFile/MP3
    ${SQUALL_ROOT}/SoundFile/Ogg
    ${SQUALL_ROOT}/../external/dshow)
  target_compile_definitions(squall_dbg PRIVATE _WINDOWS _USRDLL SQUALL_EXPORTS WIN32
    DIRECTSOUND_VERSION=0x0800 SQUALL_DEBUG=1)
  target_link_libraries(squall_dbg PRIVATE squall_codec dsound dxguid winmm ole32 user32
    "${SQUALL_ROOT}/../external/dshow/amstrmid.lib")
  set_target_properties(squall_dbg PROPERTIES OUTPUT_NAME Squall
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/dbg_squall"
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
endif()
