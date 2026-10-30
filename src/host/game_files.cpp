#include "game_files.h"

#include <windows.h>

#include <cstdlib>

namespace host {

namespace {

Pak g_pak;
bool g_open = false;
std::string g_path;

std::string ExeDir() {
  char buf[MAX_PATH];
  DWORD n = GetModuleFileNameA(nullptr, buf, MAX_PATH);
  std::string s(buf, n);
  size_t p = s.find_last_of("\\/");
  return p == std::string::npos ? std::string(".") : s.substr(0, p + 1);
}

}  // namespace

bool OpenGamePak() {
  if (g_open) return true;
  char buf[MAX_PATH];
  DWORD n = GetEnvironmentVariableA("HOST_DATA", buf, MAX_PATH);
  g_path = (n > 0 && n < MAX_PATH) ? std::string(buf) : ExeDir() + "data";
  DWORD attr = GetFileAttributesA(g_path.c_str());
  if (attr != INVALID_FILE_ATTRIBUTES && (attr & FILE_ATTRIBUTE_DIRECTORY)) g_path += "\\data";
  g_open = g_pak.Open(g_path);
  return g_open;
}

const Pak& GamePak() { return g_pak; }

std::string GamePakPath() { return g_path; }

}  // namespace host
