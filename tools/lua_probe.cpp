/* Lua 绑定桩 harness —— T6.3 的仪器：在不接宿主的情况下把一关的脚本跑起来，
 * 把 144 个绑定调用逐条落成 JSONL（名字 + 实参 + 桩返回），用来和原版对拍。
 *
 * 用法（构建：cmake --build build --config Release --target lua_probe）:
 *   build/tools/Release/lua_probe.exe --csv mapping/lua-bindings.csv \
 *       --dir work/pak_gametop --out work/lua_probe_e0.jsonl \
 *       --scripts basefs.lua,lvl_o0.lua,lvl_e0.lua \
 *       --entries BaseFsBeforeCreate,Create,AttachScripts
 *
 * 判据 / 覆盖边界（读结论前必看）:
 *   - 这是**桩**：绑定语义未知（F201 只有形态），所以返回值是约定，不是原版值。
 *     `Add_*` 返回递增 id（从 1000 起），其余返回 0；返回**个数**从脚本里的
 *     多值赋值（如 `local a,b,c,d = Get_ScreenViewerRect()`）自动推出（只认
 *     单行赋值，跨行写法会退回 1）。
 *   - 能回答的问题：脚本加载是否报错、初始化调用了哪些绑定、参数是什么、
 *     对象的创建顺序。不能回答：返回值的真实语义、事件回调时序。
 *   - 错误一律打印到 stderr 并以非 0 退出（脚本语法/运行期错误不许静默）。
 *   - 输出按调用顺序，不排序：顺序本身是契约（初始化顺序，F180）。
 */
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <cmath>
#include <map>
#include <string>
#include <vector>

extern "C" {
#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"
}

static FILE* g_log = NULL;
static int g_nextId = 1000;
static long g_calls = 0;

static void JsonEscape(const char* s) {
    for (; *s; ++s) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') { fputc('\\', g_log); fputc(c, g_log); }
        else if (c == '\n') fputs("\\n", g_log);
        else if (c == '\r') fputs("\\r", g_log);
        else if (c == '\t') fputs("\\t", g_log);
        else if (c < 0x20) fprintf(g_log, "\\u%04x", c);
        else fputc(c, g_log);
    }
}

static int l_stub(lua_State* L) {
    const char* name = lua_tostring(L, lua_upvalueindex(1));
    int arity = (int)lua_tointeger(L, lua_upvalueindex(2));
    int n = lua_gettop(L);
    int ret = 0;
    if (arity < 1) arity = 1;
    ++g_calls;
    fprintf(g_log, "{\"call\":\"%s\",\"args\":[", name ? name : "?");
    for (int i = 1; i <= n; ++i) {
        if (i > 1) fputc(',', g_log);
        switch (lua_type(L, i)) {
        case LUA_TNUMBER: {
            double d = (double)lua_tonumber(L, i);
            /* Lua 表达式会算出 NaN/Inf（如 0/0）；printf 的 "-nan(ind)" 不是合法 JSON */
            if (std::isfinite(d)) fprintf(g_log, "%.9g", d);
            else fputs("null", g_log);
            break;
        }
        case LUA_TSTRING:
            fputc('"', g_log);
            JsonEscape(lua_tostring(L, i));
            fputc('"', g_log);
            break;
        case LUA_TBOOLEAN:
            fputs(lua_toboolean(L, i) ? "true" : "false", g_log);
            break;
        case LUA_TNIL:
            fputs("null", g_log);
            break;
        default:
            fprintf(g_log, "\"<%s>\"", lua_typename(L, lua_type(L, i)));
            break;
        }
    }
    if (name && strncmp(name, "Add_", 4) == 0) ret = ++g_nextId;
    fprintf(g_log, "],\"ret\":%d}\n", ret);
    lua_pushinteger(L, ret);
    for (int i = 1; i < arity; ++i) lua_pushinteger(L, 0);
    return arity;
}

static int Fail(const char* what, const char* detail) {
    fprintf(stderr, "%s: %s\n", what, detail ? detail : "(no detail)");
    return 2;
}

static bool ReadCsv(const char* csv, std::vector<std::string>* names, std::string* err) {
    FILE* f = fopen(csv, "rb");
    char line[512];
    if (!f) { *err = csv; return false; }
    if (!fgets(line, sizeof line, f)) { fclose(f); *err = "empty csv"; return false; }
    while (fgets(line, sizeof line, f)) {
        char* comma = strchr(line, ',');
        if (!comma) continue;
        *comma = 0;
        if (!line[0] || line[0] == '\r' || line[0] == '\n') continue;
        names->push_back(line);
    }
    fclose(f);
    if (names->empty()) { *err = "no binding names in csv"; return false; }
    return true;
}

/* 从脚本的多值赋值推绑定的返回个数：`local a,b,c,d = Get_ScreenViewerRect()` → 4。
 * 只认单行赋值；查不到的名字按 1 个返回（少给返回值会让脚本对 nil 做算术）。 */
static void ScanArity(const std::vector<std::string>& files,
                      const std::map<std::string, int>& known,
                      std::map<std::string, int>* arity) {
    for (size_t k = 0; k < files.size(); ++k) {
        FILE* f = fopen(files[k].c_str(), "rb");
        char line[1024];
        if (!f) continue;
        while (fgets(line, sizeof line, f)) {
            char* p = line;
            char* eq;
            int lhs = 1;
            bool clean = true;
            char name[128];
            int n = 0;
            while (*p == ' ' || *p == '\t') ++p;
            if (!strncmp(p, "local ", 6)) p += 6;
            eq = strchr(p, '=');
            if (!eq || eq[1] == '=') continue;
            for (char* q = p; q < eq; ++q) {
                if (*q == ',') ++lhs;
                else if (*q == ' ' || *q == '\t' || *q == '\r' || *q == '\n') continue;
                else if (!isalnum((unsigned char)*q) && *q != '_') clean = false;
            }
            if (!clean) continue;
            p = eq + 1;
            while (*p == ' ' || *p == '\t') ++p;
            while ((isalnum((unsigned char)*p) || *p == '_') && n < 127) name[n++] = *p++;
            name[n] = 0;
            while (*p == ' ' || *p == '\t') ++p;
            if (*p != '(' || !known.count(name)) continue;
            if ((*arity)[name] < lhs) (*arity)[name] = lhs;
        }
        fclose(f);
    }
}

static void RegisterAll(lua_State* L, const std::vector<std::string>& names,
                        const std::map<std::string, int>& arity) {
    for (size_t i = 0; i < names.size(); ++i) {
        std::map<std::string, int>::const_iterator it = arity.find(names[i]);
        lua_pushstring(L, names[i].c_str());
        lua_pushinteger(L, it == arity.end() ? 1 : it->second);
        lua_pushcclosure(L, l_stub, 2);
        lua_setglobal(L, names[i].c_str());
    }
    fprintf(stderr, "registered=%d bindings\n", (int)names.size());
}

static bool RunFile(lua_State* L, const std::string& dir, const char* leaf, std::string* err) {
    std::string path = dir + "/" + leaf;
    if (luaL_loadfile(L, path.c_str()) != 0 || lua_pcall(L, 0, LUA_MULTRET, 0) != 0) {
        *err = std::string(leaf) + ": " + lua_tostring(L, -1);
        lua_pop(L, 1);
        return false;
    }
    return true;
}

static bool RunEntry(lua_State* L, const char* name, std::string* err) {
    lua_getglobal(L, name);
    if (!lua_isfunction(L, -1)) {
        lua_pop(L, 1);
        *err = std::string(name) + " is not a function";
        return false;
    }
    if (lua_pcall(L, 0, 0, 0) != 0) {
        *err = std::string(name) + ": " + lua_tostring(L, -1);
        lua_pop(L, 1);
        return false;
    }
    return true;
}

static std::vector<std::string> Split(const char* s) {
    std::vector<std::string> out;
    const char* p = s;
    while (*p) {
        const char* q = strchr(p, ',');
        if (!q) q = p + strlen(p);
        if (q > p) out.push_back(std::string(p, (size_t)(q - p)));
        if (!*q) break;
        p = q + 1;
    }
    return out;
}

int main(int argc, char** argv) {
    const char* csv = "mapping/lua-bindings.csv";
    const char* dir = "work/pak_gametop";
    const char* out = "work/lua_probe.jsonl";
    const char* scripts = "";
    const char* entries = "";
    std::string err;
    std::vector<std::string> leaves;
    std::vector<std::string> files;
    std::vector<std::string> names;
    std::map<std::string, int> known;
    std::map<std::string, int> arity;

    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--csv") && i + 1 < argc) csv = argv[++i];
        else if (!strcmp(argv[i], "--dir") && i + 1 < argc) dir = argv[++i];
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) out = argv[++i];
        else if (!strcmp(argv[i], "--scripts") && i + 1 < argc) scripts = argv[++i];
        else if (!strcmp(argv[i], "--entries") && i + 1 < argc) entries = argv[++i];
        else return Fail("usage", "--csv/--dir/--out/--scripts/--entries");
    }
    leaves = Split(scripts);

    g_log = fopen(out, "wb");
    if (!g_log) return Fail("cannot open out", out);

    lua_State* L = luaL_newstate();
    if (!L) { fclose(g_log); return Fail("luaL_newstate", "null"); }
    luaL_openlibs(L);
    if (!ReadCsv(csv, &names, &err)) { lua_close(L); fclose(g_log); return Fail("csv", err.c_str()); }
    for (size_t i = 0; i < names.size(); ++i) known[names[i]] = 1;
    for (size_t i = 0; i < leaves.size(); ++i) files.push_back(std::string(dir) + "/" + leaves[i]);
    ScanArity(files, known, &arity);
    RegisterAll(L, names, arity);

    for (size_t i = 0; i < leaves.size(); ++i) {
        if (!RunFile(L, dir, leaves[i].c_str(), &err)) {
            lua_close(L); fclose(g_log); return Fail("script", err.c_str());
        }
    }
    for (size_t i = 0; i < Split(entries).size(); ++i) {
        if (!RunEntry(L, Split(entries)[i].c_str(), &err)) {
            lua_close(L); fclose(g_log); return Fail("entry", err.c_str());
        }
    }
    lua_close(L);
    fclose(g_log);
    fprintf(stderr, "calls=%ld objects=%d\n", g_calls, g_nextId - 1000);
    return 0;
}
