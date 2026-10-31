"""T7.0 跨模块 RTL 探针：FPC 2.2.4 的堆与异常在 exe/DLL 边界上的实测。

背景
----
FPC 2.2.4 Win32 的 `sysheap.inc` 只提供 `SysOSAlloc/SysOSFree`（= HeapAlloc/HeapFree
(GetProcessHeap)），真正跑的是 `heap.inc` 的通用堆：每个模块私有 freelist、16 B block
header、32 KB OS chunk、`MaxKeptOSChunks=4`。跨模块 GetMem/FreeMem 只是块头布局恰好相同，
块会挂到**释放方**的 freelist；chunk 计数在共享头里，释放方可能把 chunk 还给进程堆，而
分配方 freelist 仍指向其中（悬垂）。异常链是 ThreadVar（`ExceptAddrStack`/`ExceptObjectStack`），
每个模块各一份。本仪器把这两件事做成可重跑的判据，而不是靠读源码推断。

用法
----
    # 1) 编 rplib.dll + rphost.exe 到 build/rtlprobe/（需要 FPC 2.2.4）
    python tools/rtlprobe_build.py --build
    # 2) 同工具链矩阵（每模式独立进程；默认模式集见 EXPECT）
    python tools/rtlprobe_build.py --same
    python tools/rtlprobe_build.py --same heapa heapb mm-heapa mm-heapb
    # 3) 真宿主（game.exe 目录，需已装 b2 代理与 b2Physics_orig.dll）
    python tools/rtlprobe_build.py --host "work/e2e_game" --mode mmrec \
        --log "work/rtl_mmrec.log"
    python tools/rtlprobe_build.py --host "work/e2e_game" --mode exc --log "work/rtl_exc.log"

真宿主路径：`build/proxy/Release/b2Physics.dll`（代理，env `B2RTLPROBE_DLL` 门控）
在主线程消息循环里用 `SetTimer` 调起 `rplib.dll!rp_host_entry`。探针跑完后游戏继续，
由脚本按日志里的 `ENTRY DONE` 或超时结束进程。宿主的 `TMemoryManager` 记录在
`0x5D5C50`、`TMemoryMutexManager` 在 `0x5D5C80`（game.exe md5 `059fd8f3…` 的 A2，
由 `code_match funcs` 逐函数 sim 0.96–1.00 得到：SysGetMem `0x40DE30`、
SysFreeMem `0x40DF70`、SysReAllocMem `0x40E150`、SysAllocMem `0x40E020`、
SysMemSize `0x40E000`、SysGetHeapStatus `0x40D5B0`、fpc_raiseexception `0x40B7C0`）。

判据
----
同工具链（`--same`）：
  heapa / heapb      默认 RTL 双向交叉 10 万次：**预期崩/挂**（反例；完整跑完 = 可疑）
  mm-heapa/mm-heapb  装宿主 MemoryManager 后：**必须 PASS**（10 万次双向）
  realloc            默认 RTL 交叉 ReAllocMem 2×2 万：**预期挂/崩**
  mm-realloc         装宿主 MM 后：**必须 PASS**
  splitctl/split     一个 32K chunk 内奇偶分开释放再两侧再分配：control 无重复；
                     交叉也只是 dups=0（简单交错被 ocRecycleFlag 保护，是负例）
  releasectl         全由一侧释放：chunk HeapSize 32768→$FFFFFFFF，宿主 0 个空闲块在其中
  release            偶数块宿主释放：chunk 同样被归还，但宿主 120 个空闲块仍落入其中 ⇒ FAIL
  exc-internal       两侧各自的 try/except 都应=1（阳性对照）

真宿主（`--host`）：
  hostonly           纯宿主 10 万次 GetMem/FreeMem：必须 PASS（证明探针通道本身不破坏堆）
  heapa / heapb      默认 RTL 双向交叉：预期崩/挂
  mmrec              读宿主 .data 的 MemoryManager + MemoryMutexManager 装进 DLL
                     （并在主线程运行）：A/B 10 万 + 交叉 realloc 2 万必须 PASS
  exc                在 DLL 的 try 里调宿主 `fpc_raiseexception`：DLL 捕获不到，进程死

覆盖边界
--------
- 只覆盖 FPC 2.2.4 i386-win32 的 `system.o` 堆/异常实现；LCL/GLScene 的对象生命周期
  （TComponent 树、TGL* 资源释放）不在其中。
- `release` 依赖固定 chunk 布局：blocksize=16、growheapsizesmall=32KB、
  MaxKeptOSChunks=4、fixedoffsetshift=16；四项任一变了，`HeapSize` 判据即失效。
- 真宿主路径只覆盖 `game.exe` 这个构建（无 ASLR、ImageBase 0x400000）；换版本/加壳
  必须重新跑 `code_match funcs` 并改 `tools/rtlprobe/rplib.lpr` 里的 RVA 常量。
- `mmrec` 在主线程运行；工作线程版本（代理早期实现）在 2 万次内崩，说明即使共享
  MemoryManager + 锁，宿主堆也默认按单线程使用（[推断] 宿主 IsMultiThread=false）。
  注入代码必须跑在宿主自己的线程上。

失效条件
--------
FPC 版本/编译开关（blocksize、-Cr/-Co）、game.exe 换版、b2 代理加载顺序或导出表变更后，
先重跑 `python tools/rtlprobe_build.py --build --same` 并对照 F244–F248。
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "rtlprobe")
OUT = os.path.join(ROOT, "build", "rtlprobe")
FPC = os.environ.get("FPC", r"C:/lazarus/fpc/2.2.4/bin/i386-win32/fpc.exe")
PROXY = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")

SAME_MODES = ["splitctl", "split", "releasectl", "release",
              "heapa", "heapb", "mm-heapa", "mm-heapb", "realloc", "mm-realloc"]
HOST_MODES = ["hostonly", "heapa", "heapb", "mmrec", "exc"]


def build():
    os.makedirs(OUT, exist_ok=True)
    for src in ("rplib.lpr", "rphost.lpr"):
        cmd = [FPC, "-Mdelphi", "-O1", "-g-", "-Xs-", "-Xm",
               "-FE" + OUT, "-FU" + OUT, os.path.join(SRC, src)]
        print("build:", " ".join(cmd))
        subprocess.run(cmd, cwd=OUT, check=True)


def run_same(modes, timeout):
    exe = os.path.join(OUT, "rphost.exe")
    dll = os.path.join(OUT, "rplib.dll")
    if not (os.path.exists(exe) and os.path.exists(dll)):
        sys.exit("缺 build/rtlprobe/{rphost.exe,rplib.dll}：先 --build")
    rows = []
    for m in modes:
        t0 = time.time()
        verdict = ""
        try:
            p = subprocess.run([exe, m], cwd=OUT, capture_output=True,
                               text=True, timeout=timeout)
            tail = [l for l in p.stdout.splitlines() if l.strip()][-4:]
            verdict = "PASS" if "RESULT PASS" in p.stdout else "FAIL"
            detail = " | ".join(tail)
        except subprocess.TimeoutExpired as e:
            verdict = "HANG"
            out = (e.stdout or b"")
            if isinstance(out, bytes):
                out = out.decode("utf-8", "replace")
            detail = "timeout %ss; last=%s" % (timeout, out.strip().splitlines()[-1:] or "")
        rows.append((m, verdict, time.time() - t0, detail))
        print("SAME %-12s %-5s %6.1fs  %s" % (m, verdict, rows[-1][2], detail))
    return rows


def patch_host_dir(gamedir):
    if not os.path.exists(os.path.join(gamedir, "b2Physics_orig.dll")):
        sys.exit("缺 %s/b2Physics_orig.dll（原版 b2Physics.dll 改名）" % gamedir)
    dll = os.path.join(OUT, "rplib.dll")
    if not os.path.exists(dll):
        sys.exit("缺 build/rtlprobe/rplib.dll：先 --build")
    if not os.path.exists(PROXY):
        sys.exit("缺 build/proxy/Release/b2Physics.dll：先构建 b2physics_proxy")
    shutil.copy2(PROXY, os.path.join(gamedir, "b2Physics.dll"))
    shutil.copy2(dll, os.path.join(gamedir, "rplib.dll"))


def run_host(gamedir, mode, log, wait):
    patch_host_dir(gamedir)
    env = os.environ.copy()
    env["B2RTLPROBE_DLL"] = os.path.join(gamedir, "rplib.dll")
    env["B2RTLPROBE_MODE"] = mode
    env["B2RTLPROBE_LOG"] = os.path.abspath(log)
    env["B2PROXY_LOG"] = os.path.join(gamedir, "b2ffi_probe.log")
    if os.path.exists(log):
        os.remove(log)
    p = subprocess.Popen([os.path.join(gamedir, "game.exe")], cwd=gamedir, env=env)
    deadline = time.time() + wait
    done = False
    while time.time() < deadline:
        time.sleep(0.5)
        if p.poll() is not None:
            break
        if os.path.exists(log):
            try:
                if "ENTRY DONE" in open(log, "rb").read().decode("utf-8", "replace"):
                    done = True
                    break
            except OSError:
                pass
    killed = p.poll() is None
    if killed:
        p.kill()
        p.wait()
    text = ""
    if os.path.exists(log):
        text = open(log, "rb").read().decode("utf-8", "replace")
    print(text)
    if done:
        bad = ("ok=False" in text) or ("host raise returned" in text)
        verdict = "FAIL" if bad else "PASS"
    elif p.returncode not in (0, None):
        verdict = "CRASH"
    else:
        verdict = "HANG"
    print("HOST %-10s %-5s killed=%s exit=%s log=%s" %
          (mode, verdict, killed, p.returncode, log))
    return verdict


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="编译 rplib.dll + rphost.exe")
    ap.add_argument("--same", nargs="*", metavar="MODE", help="同工具链矩阵")
    ap.add_argument("--same-timeout", type=int, default=60)
    ap.add_argument("--host", metavar="GAMEDIR", help="game.exe 所在目录")
    ap.add_argument("--mode", default="hostonly", help="真宿主模式（见 docstring）")
    ap.add_argument("--log", default=os.path.join(ROOT, "work", "rtlprobe.log"))
    ap.add_argument("--wait", type=int, default=180, help="真宿主最长等待秒数")
    a = ap.parse_args()
    if a.build:
        build()
    if a.same is not None or (not a.host and not a.build):
        modes = a.same if a.same else SAME_MODES
        run_same(modes, a.same_timeout)
    if a.host:
        run_host(a.host, a.mode, a.log, a.wait)


if __name__ == "__main__":
    main()
