# Lua 5.1.5（vendor 快照）

- 来源：<https://www.lua.org/ftp/lua-5.1.5.tar.gz>，md5 `2e115fe26e435e33b0d5c022e4490567`。
- 只取 `src/*.c` / `src/*.h` + 上游 `COPYRIGHT` / `README`。
- **代码未改动**；仅按仓库换行约定（F130：追踪文本统一 CRLF）把源码换行从 LF 转成 CRLF，
  与 `vendor/box2d-2.0.2` 的处理方式相同。
- 许可证：MIT（见 `COPYRIGHT`）。
- 用途：宿主 `src/host/lua_scripts.cpp` 用 `luaL_loadbuffer` 编译 pak 里的关卡脚本，
  `luac` 作为 `tools/check_lua.py` 的语法判据（依据 docs/facts.md F04、F191）。
