"""用宿主自带的 Lua 5.1.5（vendor，未改动）把 pak 里的脚本全量编译一遍。

用法:
  python tools/check_lua.py [目录]        # 默认 work/pak_gametop（tools/pak.py extract 的产物）
判据:
  所有 .lua 都必须编译通过（luac -p 退出码 0）；任何一条失败即非 0 退出并打印首个错误。
意义:
  证明「VM 版本对（游戏逻辑是 Lua 5.1，F04）、脚本文本能原样喂进 Lua 5.1.5」。
  执行这些脚本还需要宿主的 144 个绑定（F180），那是 T3.3 的后续切片——本条**不覆盖**执行语义。
依赖:
  build/tools/Release/luac.exe（cmake --build build --config Release --target luac）
依据: docs/facts.md F04、F180、F191。
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LUAC = os.path.join(ROOT, "build", "tools", "Release", "luac.exe")


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work", "pak_gametop")
    if not os.path.exists(LUAC):
        raise SystemExit("缺 %s（cmake --build build --config Release --target luac）" % LUAC)
    files = sorted(glob.glob(os.path.join(d, "*.lua")))
    if not files:
        raise SystemExit("目录里没有 .lua：%s" % d)
    bad = []
    for f in files:
        p = subprocess.run([LUAC, "-p", f], capture_output=True, text=True)
        if p.returncode != 0:
            bad.append((os.path.basename(f), (p.stderr or p.stdout).strip().splitlines()[:1]))
    print("lua files=%d compiled=%d failed=%d" % (len(files), len(files) - len(bad), len(bad)))
    for name, msg in bad[:10]:
        print("  FAIL %s: %s" % (name, msg))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
