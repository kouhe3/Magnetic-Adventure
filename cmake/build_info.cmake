# 构建指纹：由 b2physics 目标的 POST_BUILD 调用，写 build/build_info.json。
#
# 目的（docs/facts.md F82/F87）：门禁与 sweep 的每一行结论都必须能回答「出自哪个构建」。
# 指纹来自 **实际产物** 的 md5，而不是命令行假设——DLL 被覆盖后指纹就对不上，
# tools/instr.py 会把这种情况记成 arch=unknown，而不是沿用旧值。
#
# 参数：OUT DLL LIB ARCH FP MSVC TOOLSET CXX CONFIG FLAGS
file(MD5 "${DLL}" dll_md5)
file(MD5 "${LIB}" box2d_md5)
string(REPLACE "\\" "/" dll_path "${DLL}")
string(REPLACE "\\" "/" box2d_path "${LIB}")
string(REPLACE "\"" "'" flags "${FLAGS}")
string(TIMESTAMP built "%Y-%m-%dT%H:%M:%S" UTC)
file(WRITE "${OUT}"
"{
  \"dll\": \"${dll_path}\",
  \"dll_md5\": \"${dll_md5}\",
  \"box2d_lib\": \"${box2d_path}\",
  \"box2d_md5\": \"${box2d_md5}\",
  \"arch\": \"${ARCH}\",
  \"fp\": \"${FP}\",
  \"config\": \"${CONFIG}\",
  \"msvc\": \"${MSVC}\",
  \"toolset\": \"${TOOLSET}\",
  \"cxx\": \"${CXX}\",
  \"flags\": \"${flags}\",
  \"built\": \"${built}\"
}
")
