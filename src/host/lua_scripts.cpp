#include "lua_scripts.h"

#include <cctype>

extern "C" {
#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"
}

#include "game_files.h"

namespace host {

namespace {

bool EndsWithLua(const std::string& name) {
  if (name.size() < 4) return false;
  const size_t n = name.size();
  return std::tolower(static_cast<unsigned char>(name[n - 4])) == '.' &&
         std::tolower(static_cast<unsigned char>(name[n - 3])) == 'l' &&
         std::tolower(static_cast<unsigned char>(name[n - 2])) == 'u' &&
         std::tolower(static_cast<unsigned char>(name[n - 1])) == 'a';
}

}  // namespace

LuaCompileStat CompilePakLua() {
  LuaCompileStat st;
  lua_State* L = luaL_newstate();
  if (!L) {
    st.failed = -1;
    st.first_error = "luaL_newstate failed";
    return st;
  }
  luaL_openlibs(L);
  const Pak& pak = GamePak();
  for (const auto& e : pak.entries()) {
    if (!EndsWithLua(e.name)) continue;
    const char* buf = reinterpret_cast<const char*>(pak.Data(e));
    if (luaL_loadbuffer(L, buf, e.size, e.name.c_str()) == 0) {
      ++st.ok;
      lua_pop(L, 1);  // 丢掉编译出来的函数
    } else {
      ++st.failed;
      if (st.first_error.empty()) {
        const char* msg = lua_tostring(L, -1);
        st.first_error = e.name + ": " + (msg ? msg : "(no message)");
      }
      lua_pop(L, 1);
    }
  }
  lua_close(L);
  return st;
}

}  // namespace host
