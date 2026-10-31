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

# ---- 转发 DLL（OpenGL）：占住 opengl32.dll 文件名，把 368 个导出尾跳给
#      opengl32_orig.dll（改名副本），记录名称/QPC/栈上 6 个实参。
#      opengl32 不在 KnownDLLs（F175）⇒ 应用目录代理能接住静态导入；
#      SwapBuffers/ChoosePixelFormat 在 gdi32（KnownDLL）⇒ 帧边界靠 gl* 时间戳推断。
#      桩由 tools/gen_proxy.py 生成：
#        python tools/gen_proxy.py --csv mapping/opengl32-exports.csv \
#          --out-c src/glproxy/proxy_stubs.c --out-def src/glproxy/proxy.def \
#          --library opengl32 --prefix ""
add_library(gl_proxy SHARED
  src/glproxy/proxy_core.c
  src/glproxy/proxy_stubs.c
  src/glproxy/proxy.def)
set_target_properties(gl_proxy PROPERTIES OUTPUT_NAME opengl32
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/proxy_gl"
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

# ---- Lua 5.1.5（vendor，未改动）----
# 依据 docs/facts.md F04：游戏逻辑是 pak 内明文 Lua 5.1 源码。宿主用自己的 Lua 跑，
# 不依赖游戏目录里的 lua51.dll（两版发行的该 DLL md5 不同，见 F12）。
set(LUA_ROOT "${CMAKE_SOURCE_DIR}/vendor/lua-5.1.5/src")
set(LUA_SRC
  ${LUA_ROOT}/lapi.c ${LUA_ROOT}/lcode.c ${LUA_ROOT}/ldebug.c ${LUA_ROOT}/ldo.c
  ${LUA_ROOT}/ldump.c ${LUA_ROOT}/lfunc.c ${LUA_ROOT}/lgc.c ${LUA_ROOT}/llex.c
  ${LUA_ROOT}/lmem.c ${LUA_ROOT}/lobject.c ${LUA_ROOT}/lopcodes.c ${LUA_ROOT}/lparser.c
  ${LUA_ROOT}/lstate.c ${LUA_ROOT}/lstring.c ${LUA_ROOT}/ltable.c ${LUA_ROOT}/ltm.c
  ${LUA_ROOT}/lundump.c ${LUA_ROOT}/lvm.c ${LUA_ROOT}/lzio.c
  ${LUA_ROOT}/lauxlib.c ${LUA_ROOT}/lbaselib.c ${LUA_ROOT}/ldblib.c ${LUA_ROOT}/liolib.c
  ${LUA_ROOT}/lmathlib.c ${LUA_ROOT}/loslib.c ${LUA_ROOT}/ltablib.c ${LUA_ROOT}/lstrlib.c
  ${LUA_ROOT}/loadlib.c ${LUA_ROOT}/linit.c)
add_library(lua51 STATIC ${LUA_SRC})
set_target_properties(lua51 PROPERTIES
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
target_include_directories(lua51 PUBLIC ${LUA_ROOT})

# lua51.dll：FPC 宿主（magnet.exe）用 `external 'lua51.dll'` 加载。
# LUA_BUILD_AS_DLL 让带 LUA_CORE/LUA_LIB 的源文件导出 lua_*（luaconf.h:154-162）；
# 导入库改名 lua51_dll.lib，避免与上面的静态库 lua51.lib 同名。
add_library(lua51_dll SHARED ${LUA_SRC})
target_compile_definitions(lua51_dll PRIVATE LUA_BUILD_AS_DLL)
target_include_directories(lua51_dll PUBLIC ${LUA_ROOT})
set_target_properties(lua51_dll PROPERTIES
  OUTPUT_NAME lua51
  ARCHIVE_OUTPUT_NAME lua51_dll
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# luac：Lua 5.1 的语法检查器/编译器；tools/check_lua.py 用它把 pak 里的脚本全量编译一遍
add_executable(luac ${LUA_ROOT}/luac.c ${LUA_ROOT}/print.c)
target_link_libraries(luac PRIVATE lua51)
set_target_properties(luac PROPERTIES OUTPUT_NAME luac
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tools"
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# lua_probe：144 个绑定的桩 harness（tools/lua_probe.cpp）。跑一关的脚本、把
# 绑定调用落成 JSONL，用于 T6.3 的"脚本能起来 + 初始化调用序"判据。
add_executable(lua_probe tools/lua_probe.cpp)
target_link_libraries(lua_probe PRIVATE lua51)
set_target_properties(lua_probe PROPERTIES OUTPUT_NAME lua_probe
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tools"
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# objlog：注入原版 game.exe 的进程内对象创建记录器（src/objlog/objlog.c）。
# 把 65 个 `call <Add_*工厂>` 点改成 thunk，靠改写返回地址记录 eax/edx，不暂停进程；
# 站点表由 `python tools/gen_objlog.py` 从 work/add_bps_all.txt 生成到 src/objlog/sites.h。
add_library(objlog SHARED src/objlog/objlog.c)
set_target_properties(objlog PROPERTIES
  OUTPUT_NAME objlog
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
target_link_libraries(objlog PRIVATE kernel32)

# ---- 宿主脚手架（T3.1）----
# 只复刻窗口/消息参数（F154/F155/F156/F158），暂不含 GL 与 pak 加载。
# 验收：tools/winprobe.py 对原版与产物各跑一次，逐字段 diff（见其 docstring）。
# 注意：**不要**给这个 exe 加 dpiAware 清单——原版就是 DPI-unaware（F154）。
add_executable(host WIN32 src/host/main.cpp src/host/gl_render.cpp
  src/host/font_table.cpp src/host/game_files.cpp src/host/levels.cpp src/host/lua_scripts.cpp
  src/host/menu_layout.cpp src/host/pak.cpp src/host/wic_decode.cpp)
set_target_properties(host PROPERTIES OUTPUT_NAME magnethost
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
target_compile_definitions(host PRIVATE UNICODE _UNICODE)
target_link_libraries(host PRIVATE user32 opengl32 glu32 windowscodecs ole32 lua51)
# 子系统版本必须写成 4.0：原版 game.exe 的 MajorSubsystemVersion=4.0（Lazarus 0.9.28 时代），
# 而 Windows 对 subsystem<6 的映像用**旧式非客户区度量**（对话框边框 3/侧、无 DWM padding），
# 这正是原版外框 1024×768 / 客户区 1018×739 的来源；用默认 6.0 会得到 8/31（F166）。
set_target_properties(host PROPERTIES LINK_FLAGS "/SUBSYSTEM:WINDOWS,5.01")

# 不嵌清单：原版 game.exe 完全没有 manifest（F154）。实测这条**不改变**非客户区边框
# （加不加清单都是 8/31，原版是 3/26），保留只是为了与原版一致。
target_link_options(host PRIVATE "/MANIFEST:NO")
