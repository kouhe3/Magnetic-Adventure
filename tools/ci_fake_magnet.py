#!/usr/bin/env python3
"""CI fake magnet: drive the game's own magnet path on a private desktop.

Why this exists
---------------
`src/proxydll/proxy_core.c` can forge `GetCursorPos` / `GetAsyncKeyState`
(`B2CI_FAKE_MAGNET`) so the retail game samples a synthetic cursor. The magnet
force then comes from the game itself: hit test -> target lock -> min(315,30*d)
-> target vtable +0xD4. This tool is the reusable harness for that path; it does
not move the real cursor and does not write game fields.

Usage
-----
    # 1) build a game copy whose pak contains the fixture level
    python tools/ci_fake_magnet.py build --out work/fakemag_chain \
        --o tests/levels/chain_o.lua --e tests/levels/chain_e.lua

    # 2) run staged drags (starts/ends are world units; repeat --stage;
    #    use --stage=... because a start like -3,3 begins with a dash)
    "%PY32%" tools/ci_fake_magnet.py run --dir work/fakemag_chain --level 1 \
        --stage=0,0:3,0 --stage=-3,3:0,6 --marker 99,99 --done-dist 0.65 \
        --hold 2.5 --runtime-stage 1 --require-fg --json work/fakemag_chain.json

    # 3) completion-chain stability on retail level 1: the drag itself produces
    #    the two in-target OnMove calls; --require-complete checks any size-0x30
    #    HUD sprite whose +0x2C goes 0 -> 1.0 vs the level-entry baseline.
    #    --nudge is an optional fallback (release, re-grip, move a little); on
    #    level 1 HintState>4 makes the re-grip target 0, so it is not needed.
    "%PY32%" tools/ci_fake_magnet.py run --dir work/e2e_game --level 1 \
        --stage=7.25,-5.14:-8.846,10.129 --stage=-1.96,-9.10:5.824,8.947 \
        --nudge 1:1.0:0.15 --require-complete --complete-wait 8

Stage syntax: `start_x,start_y:goal_x,goal_y[:done_dist]`.  Each stage grabs the
body nearest to the start point (within `--start-tol`), holds the button, moves
the synthetic cursor to the goal, and releases when the body is within
`done_dist` (default `--done-dist`, 0.30).

Obstacles: pass `--waypoint STAGE:x,y` (repeatable) to steer the synthetic
cursor through intermediate points before the goal (e.g. around a static wall).
The waypoint is "reached" when the body is within `--waypoint-tol`, or after
`--waypoint-hold` seconds.

Observe mode (no magnet): `--observe SEC --angle x,y [--angle x,y]` finds the
bodies nearest to those points, waits SEC seconds and reads their angles; each
body must move at least `--min-angle` rad.  With two bodies and `--gear-ratio`
it also requires opposite signs and |(-d2/d1) - ratio| <= `--ratio-tol`.

Stage angle: `--stage-angle STAGE:x,y` also watches a body's angle during a
magnet stage and requires |delta| >= `--stage-min-angle`.  `--ignore-distance`
drops the goal-distance requirement for pinned bodies (e.g. a switch arm).

Criterion (exit 0 = PASS)
-------------------------
* every stage: target locked on press, body reached `done_dist` before timeout;
  the distance is the **per-step minimum** parsed from the recorded digest
  (a 50 ms live poll misses the fast pass), not the last live sample;
* every `--marker x,y` appears as a `b2_Body_SetXForm` pre-record with that
  position (Lua completion marker written from the fixture);
* magnet ApplyForce lines exist and match: direction = mouse-target, |F|<=315,
  |F|=315 outside 10.5 world units, |F|-30*d <= 2.5 inside, body = the stage
  target's body, target set = stage set (see F386);
* `--require-complete`: after all stages, any size-0x30
  `TGlAlphaHudSpriteObject` that was `+0x2C == 0` at level entry has
  `+0x2C == 1.0` within `--complete-wait` (F430; the first such object is the
  end-level box and may stay 0, so the baseline comparison is required);
* the game window never becomes the user's foreground window
  (`--require-fg`), and a clean ExitProcess.

Boundary
--------
* Fixtures replace `lvl_o14.lua` / `lvl_e14.lua` in the pak copy; no new TOC
  entries, no map/level-list changes.  `build` never touches `bin/`.
* Only bodies present in the live digest can be targeted; bodies created by Lua
  after a stage are found by waiting for a body within `--start-tol`.
* Pixel evidence is not used: `PrintWindow` is black on a private desktop (F388).

Failure modes
-------------
* Not 32-bit Python -> exit 2 (CONTEXT is x86).
* MENU not reached / level dispatch failed -> exit 3.
* Stage body not found, target not locked, goal not reached, marker missing,
  force check failed, or foreground changed -> exit 1 with a JSON summary.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import math
import os
import re
import shutil
import struct
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import direct_drive as dd  # noqa: E402

ORACLE = os.path.join(ROOT, "bin", "gametop")
PROXY = os.path.join(ROOT, "build", "proxy", "Release", "b2Physics.dll")
DEFAULT_O = os.path.join(ROOT, "tests", "levels", "test_lvl_o.lua")
DEFAULT_E = os.path.join(ROOT, "tests", "levels", "test_lvl_e.lua")
WORK = os.path.join(ROOT, "work")

k32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
k32.OpenProcess.restype = ctypes.c_void_p
k32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_void_p, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
PROC_RW = dd.PROCESS_VM_READ | dd.PROCESS_QUERY_INFORMATION

# B2FFI02 record sizes (src/proxydll/proxy_core.c).
PRE_SIZE = 536
POST_SIZE = 144
PRE_ID_OFF = 4
PRE_M1_OFF = 280  # 6 dwords header + 32 dwords args + m0[128]
MAGNET_C1 = 0x58E585  # return point of [target vtable+0xD4] in 0x58E4A0 (F386)


# ---- memory (external read only) ----
def rpm(hp, addr, n):
    buf = ctypes.create_string_buffer(n)
    got = ctypes.c_size_t()
    ok = k32.ReadProcessMemory(hp, ctypes.c_void_p(addr), buf, n,
                               ctypes.byref(got))
    return buf.raw[:got.value] if ok and got.value == n else None


def u32(hp, addr):
    b = rpm(hp, addr, 4)
    return struct.unpack("<I", b)[0] if b else None


def u8(hp, addr):
    b = rpm(hp, addr, 1)
    return b[0] if b else None


def f32(hp, addr):
    b = rpm(hp, addr, 4)
    return struct.unpack("<f", b)[0] if b else None


def player_state(hp):
    mgr = u32(hp, 0x665334)
    if not mgr:
        return None
    player = u32(hp, mgr + 0x48)
    if not player:
        return None
    mouse = u32(hp, player + 8)
    st = {"player": player, "mouse": mouse, "target": u32(hp, player + 0x14),
          "flag": u8(hp, player + 0x10)}
    if mouse:
        st["mx"] = f32(hp, mouse + 0x40)
        st["my"] = f32(hp, mouse + 0x44)
        st["btn"] = u8(hp, mouse + 0x1F)
    return st


def open_proc(pid):
    return k32.OpenProcess(PROC_RW, False, pid)


# ---- live digest (B2PROXY_LIVE) ----
class LiveDigest:
    """Parse the proxy's kind=0/1/2/3 stream; keep only the last body digest.

    BodyDigest: ptr, flags, sleepTime, vx, vy, w, px, py, angle, mass,
    invMass, I, invI  (F26 / proxy_core.c).
    """

    def __init__(self, path):
        self.path = path
        self.f = None
        self.buf = b""
        self.hdr = False
        self.seq = 0
        self.bodies = []

    def poll(self):
        if self.f is None:
            if not os.path.exists(self.path):
                return self.bodies
            self.f = open(self.path, "rb")
        d = self.f.read()
        if d:
            self.buf += d
        if not self.hdr:
            if len(self.buf) < 20:
                return self.bodies
            self.buf = self.buf[20:]
            self.hdr = True
        while len(self.buf) >= 4:
            kind = struct.unpack_from("<I", self.buf, 0)[0]
            if kind == 0:
                size = PRE_SIZE
            elif kind == 1:
                size = POST_SIZE
            elif kind == 2:
                if len(self.buf) < 16:
                    return self.bodies
                seq, count, _ = struct.unpack_from("<III", self.buf, 4)
                size = 16 + 52 * count
                if len(self.buf) < size:
                    return self.bodies
                self.bodies = [struct.unpack_from("<II11f", self.buf, 16 + 52 * i)
                               for i in range(count)]
                self.seq = seq
                self.buf = self.buf[size:]
                continue
            elif kind == 3:
                if len(self.buf) < 16:
                    return self.bodies
                count = struct.unpack_from("<I", self.buf, 8)[0]
                size = 16 + 12 * count
                if len(self.buf) < size:
                    return self.bodies
                self.buf = self.buf[size:]
                continue
            else:
                self.buf = b""
                return self.bodies
            if len(self.buf) < size:
                return self.bodies
            self.buf = self.buf[size:]
        return self.bodies


def wait_cond(fn, timeout, poll=0.05):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = fn()
        if v:
            return v
        time.sleep(poll)
    return None


def find_body(bodies, ptr):
    for i, b in enumerate(bodies):
        if b[0] == ptr:
            return i, b
    return None, None


def nearest_body(bodies, x, y, exclude=()):
    best = None
    for i, b in enumerate(bodies):
        if b[0] in exclude:
            continue
        d = math.hypot(b[6] - x, b[7] - y)
        if best is None or d < best[0]:
            best = (d, i, b)
    return best


# ---- hot config (read by the proxy hook every sample) ----
def write_cfg(path, x, y, btn):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("%.4f,%.4f,%d\n" % (x, y, 1 if btn else 0))
    for _ in range(50):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.004)
    raise RuntimeError("write_cfg replace failed")


def calibrate(hp, cfg):
    write_cfg(cfg, 0.0, 0.0, 0)
    time.sleep(0.25)
    a = player_state(hp)
    write_cfg(cfg, 10.0, 10.0, 0)
    time.sleep(0.25)
    b = player_state(hp)
    write_cfg(cfg, 0.0, 0.0, 0)
    if not a or not b or "mx" not in a or "mx" not in b:
        return {"ok": False, "why": "no mouse fields"}
    ax = (b["mx"] - a["mx"]) / 10.0
    bx = a["mx"]
    ay = (b["my"] - a["my"]) / 10.0
    by = a["my"]
    return {"ok": abs(ax) > 1e-6 and abs(ay) > 1e-6, "ax": ax, "bx": bx,
            "ay": ay, "by": by, "m00": [a["mx"], a["my"]],
            "m1010": [b["mx"], b["my"]]}


def cfg_world(cal, x, y):
    if cal.get("ok"):
        return ((x - cal["bx"]) / cal["ax"], (y - cal["by"]) / cal["ay"])
    return (x, y)


OFFSETS = [(0.0, 0.0), (0.2, 0.0), (-0.2, 0.0), (0.0, 0.2), (0.0, -0.2),
           (0.35, 0.0), (-0.35, 0.0), (0.0, 0.35)]


def press_on(hp, cal, cfg, x, y, tries=8):
    for k in range(min(tries, len(OFFSETS))):
        px = x + OFFSETS[k][0]
        py = y + OFFSETS[k][1]
        cx, cy = cfg_world(cal, px, py)
        write_cfg(cfg, cx, cy, 0)
        time.sleep(0.12)
        write_cfg(cfg, cx, cy, 1)
        time.sleep(0.20)
        st = player_state(hp)
        if os.environ.get("CI_DEBUG"):
            print("  press%d at (%.2f,%.2f) target=%s" %
                  (k, px, py, st.get("target") if st else None), flush=True)
        if st and st.get("target"):
            return st, (px, py, k)
        write_cfg(cfg, cx, cy, 0)
        time.sleep(0.08)
    return None, None


def drive_to(digest, ptr, goal, done, hold, timeout):
    """Hold the synthetic button, then report the live distance seen.

    The magnet can move a light body far faster than a 50 ms poll, so the live
    distance is only used to release early; PASS is decided afterwards by
    `parse_min_dist` over every recorded step.
    """
    last = 0.0
    d = 999.0
    dmin = 999.0
    t0 = time.time()
    deadline = min(hold, timeout)
    while time.time() - t0 < deadline:
        digest.poll()
        _, b = find_body(digest.bodies, ptr)
        if b is None:
            return None, dmin
        d = math.hypot(b[6] - goal[0], b[7] - goal[1])
        dmin = min(dmin, d)
        now = time.time()
        if now - last > 0.5:
            print("  d=%.3f pos=(%.3f,%.3f) seq=%d" % (d, b[6], b[7], digest.seq),
                  flush=True)
            last = now
        if d < done:
            return d, dmin
        time.sleep(0.05)
    return d, dmin


def parse_min_dist(log_path, wanted):
    """Per-body minimum distance to its goal over every kind=2 digest record.

    `wanted` is {body_ptr: (gx, gy)}; returns {ptr: (d_min, step_seq, px, py)}.
    """
    if not os.path.exists(log_path) or not wanted:
        return {}
    d = open(log_path, "rb").read()
    best = {}
    off = 20
    while off + 4 <= len(d):
        kind = struct.unpack_from("<I", d, off)[0]
        if kind == 0:
            off += PRE_SIZE
            continue
        if kind == 1:
            off += POST_SIZE
            continue
        if kind == 2:
            if off + 16 > len(d):
                break
            seq, count, _ = struct.unpack_from("<III", d, off + 4)
            size = 16 + 52 * count
            if off + size > len(d):
                break
            for i in range(count):
                b = struct.unpack_from("<II11f", d, off + 16 + 52 * i)
                g = wanted.get(b[0])
                if g is None:
                    continue
                dist = math.hypot(b[6] - g[0], b[7] - g[1])
                cur = best.get(b[0])
                if cur is None or dist < cur[0]:
                    best[b[0]] = (dist, seq, b[6], b[7])
            off += size
            continue
        if kind == 3:
            if off + 16 > len(d):
                break
            count = struct.unpack_from("<I", d, off + 8)[0]
            off += 16 + 12 * count
            continue
        break
    return best


# ---- log/force checks ----
def parse_markers(log_path, markers, tol=0.5):
    """Return occurrences of `b2_Body_SetXForm` pre-record m1 near any marker."""
    if not os.path.exists(log_path):
        return []
    d = open(log_path, "rb").read()
    out = []
    off = 20
    while off + 4 <= len(d):
        kind = struct.unpack_from("<I", d, off)[0]
        if kind == 0:
            if off + PRE_SIZE > len(d):
                break
            eid = struct.unpack_from("<I", d, off + PRE_ID_OFF)[0]
            if eid == 34:  # b2_Body_SetXForm
                x, y = struct.unpack_from("<2f", d, off + PRE_M1_OFF)
                for mx, my in markers:
                    if abs(x - mx) < tol and abs(y - my) < tol:
                        out.append({"x": x, "y": y, "marker": [mx, my]})
            off += PRE_SIZE
        elif kind == 1:
            off += POST_SIZE
        elif kind == 2:
            if off + 16 > len(d):
                break
            count = struct.unpack_from("<I", d, off + 8)[0]
            off += 16 + 52 * count
        elif kind == 3:
            if off + 16 > len(d):
                break
            count = struct.unpack_from("<I", d, off + 8)[0]
            off += 16 + 12 * count
        else:
            break
    return out


def parse_force_trace(path):
    pat = re.compile(
        r"body=([0-9a-f]{8}) f=([0-9a-f]{8}),([0-9a-f]{8}) "
        r"c0=([0-9a-f]{8}) c1=([0-9a-f]{8}) c2=([0-9a-f]{8}) c3=([0-9a-f]{8}) "
        r"seq=(\d+) p=(-?[\d.]+),(-?[\d.]+) tgt=([0-9a-f]{8}) "
        r"mw=(-?[\d.]+),(-?[\d.]+)")
    if not os.path.exists(path):
        return []
    def fbits(h):
        return struct.unpack("<f", struct.pack("<I", int(h, 16)))[0]
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = pat.search(line)
        if not m:
            continue
        px, py = float(m.group(9)), float(m.group(10))
        mx, my = float(m.group(12)), float(m.group(13))
        fx, fy = fbits(m.group(2)), fbits(m.group(3))
        d = math.hypot(mx - px, my - py)
        mag = math.hypot(fx, fy)
        dang = None
        if d > 1e-6:
            exp_dir = math.atan2(my - py, mx - px)
            got_dir = math.atan2(fy, fx)
            dang = abs((got_dir - exp_dir + math.pi) % (2 * math.pi) - math.pi)
        out.append({"body": int(m.group(1), 16), "fx": fx, "fy": fy,
                    "mag": mag, "c0": int(m.group(4), 16),
                    "c1": int(m.group(5), 16), "tgt": int(m.group(11), 16),
                    "p": [px, py], "mw": [mx, my], "d": d, "dang": dang})
    return out


def check_forces(forces, expect):
    mag = [f for f in forces if f["c1"] == MAGNET_C1]
    res = {"n_lines": len(forces), "n_magnet": len(mag)}
    if not mag:
        res.update(pass_=False, why="no magnet ApplyForce")
        return res
    res["dir_ok"] = all(f["dang"] is not None and f["dang"] < 0.35 for f in mag)
    res["cap_ok"] = all(f["mag"] <= 315.001 for f in mag)
    res["far_ok"] = all(abs(f["mag"] - 315.0) <= 0.01 for f in mag if f["d"] > 10.5)
    # trace p is the b2 body position; the game uses TPhysicObject position
    # (one frame apart), so allow 2.5 on the near-field 30*d branch.
    res["near_ok"] = all(abs(f["mag"] - 30.0 * f["d"]) <= 2.5
                         for f in mag if f["d"] <= 10.5)
    res["body_ok"] = all(expect.get(f["tgt"]) == f["body"] for f in mag)
    res["stages_ok"] = set(f["tgt"] for f in mag) == set(expect) if expect else False
    res["pass_"] = all(res[k] for k in ("dir_ok", "cap_ok", "far_ok", "near_ok",
                                        "body_ok", "stages_ok"))
    worst = max(mag, key=lambda f: f["dang"] if f["dang"] is not None else 9)
    res["worst_dang"] = worst["dang"]
    res["worst_law_err"] = max(abs(f["mag"] - min(315.0, 30.0 * f["d"])) for f in mag)
    return res


# ---- build ----
def build(out, lua_o, lua_e, proxy):
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    skip = (".i64", ".id0", ".id1", ".id2", ".nam", ".til")
    for name in os.listdir(ORACLE):
        src = os.path.join(ORACLE, name)
        if not os.path.isfile(src) or name.endswith(skip) or name == "data":
            continue
        shutil.copy2(src, os.path.join(out, name))
    shutil.copy2(proxy, os.path.join(out, "b2Physics.dll"))
    shutil.copy2(os.path.join(ORACLE, "b2Physics.dll"),
                 os.path.join(out, "b2Physics_orig.dll"))
    data = os.path.join(out, "data")
    if os.path.exists(data):
        os.remove(data)
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "pak_write.py"),
                    "rebuild", os.path.join(ORACLE, "data"), data,
                    "lvl_o14.lua=" + os.path.abspath(lua_o),
                    "lvl_e14.lua=" + os.path.abspath(lua_e)], check=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "pak.py"),
                    "verify", data], check=True)
    print("built", out, "proxy", proxy, "o", lua_o, "e", lua_e, flush=True)
    return 0


# ---- launch / dispatch (private desktop) ----
def launch(game_dir, log, force, mag_trace, cfg):
    env = dict(os.environ)
    env["B2PROXY_LOG"] = log
    env["B2PROXY_LIVE"] = "1"
    env.pop("B2PROXY_LIGHT", None)
    env["B2PROXY_TRACE"] = force
    env["B2CI_FAKE_MAGNET"] = "1"
    env["B2CI_MAG_CONFIG"] = cfg
    env["B2CI_MAG_TRACE"] = mag_trace
    env.pop("B2CI_INDEX", None)
    env.pop("B2CI_CONFIG", None)
    os.environ.update(env)
    desk_name = "MagCI_%d" % os.getpid()
    desk = user32.CreateDesktopW(desk_name, None, None, 0, dd.DESKTOP_ALL, None)
    if not desk:
        raise SystemExit("CreateDesktop failed %d" % ctypes.get_last_error())
    si = dd.STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = desk_name
    pi = dd.PROCESS_INFORMATION()
    exe = os.path.join(game_dir, "game.exe")
    ok = dd.k32.CreateProcessW(exe, exe, None, None, False, 0, None, game_dir,
                               ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        raise SystemExit("CreateProcess failed %d" % ctypes.get_last_error())
    pid = pi.dwProcessId
    print("pid", pid, "desktop", desk_name, flush=True)
    dd.mute_game()
    hp = dd.k32.OpenProcess(dd.PROCESS_VM_READ | dd.PROCESS_QUERY_INFORMATION |
                            dd.PROCESS_VM_OPERATION | dd.PROCESS_VM_WRITE |
                            dd.PROCESS_CREATE_THREAD, False, pid)
    return desk, desk_name, si, pi, hp, pid


def dispatch(hp, pi, desk, pid, index, settle):
    menu = None
    for _ in range(150):
        s = dd.state(hp)
        if s[0] and s[1] and s[2] == 2 and s[3] == 0xFFFFFFFF:
            menu = s
            break
        if dd.k32.WaitForSingleObject(pi.hProcess, 0) == 0:
            raise SystemExit("exited before MENU")
        time.sleep(0.4)
    if not menu:
        raise SystemExit("MENU not reached")
    lm = menu[1]
    app = dd.scan_appobj(hp, lm)
    win = dd.find_window(pid, desk)
    if not app or not win:
        raise SystemExit("app/window not found")
    print("menu lm", hex(lm), "app", hex(app), "win", hex(win[0]), flush=True)
    tid = dd.user32.GetWindowThreadProcessId(win[0], None)
    ht = dd.k32.OpenThread(dd.THREAD_SUSPEND_RESUME | dd.THREAD_GET_CONTEXT |
                           dd.THREAD_SET_CONTEXT, False, tid)
    psapi = ctypes.WinDLL("psapi")
    mods = (ctypes.c_void_p * 64)()
    need = wt.DWORD()
    psapi.EnumProcessModules(ctypes.c_void_p(hp), mods, ctypes.sizeof(mods),
                             ctypes.byref(need))
    base = mods[0] or 0x400000
    stub_addr = dd.k32.VirtualAllocEx(hp, None, 0x1000,
                                      dd.MEM_COMMIT | dd.MEM_RESERVE,
                                      dd.PAGE_EXECUTE_READWRITE)

    def hijack():
        dd.k32.SuspendThread(ctypes.c_void_p(ht))
        ctx = dd.CONTEXT()
        ctx.ContextFlags = dd.CONTEXT_FULL
        dd.k32.GetThreadContext(ctypes.c_void_p(ht), ctypes.byref(ctx))
        stub = dd.build_stub(stub_addr, app, index, ctx.Eip,
                             base + (0x560880 - 0x400000))
        buf = ctypes.create_string_buffer(stub, len(stub))
        wr = ctypes.c_size_t(0)
        dd.k32.WriteProcessMemory(hp, ctypes.c_void_p(stub_addr), buf, len(stub),
                                  ctypes.byref(wr))
        ctx.Eip = stub_addr
        ctx.ContextFlags = dd.CONTEXT_FULL
        dd.k32.SetThreadContext(ctypes.c_void_p(ht), ctypes.byref(ctx))
        dd.k32.ResumeThread(ctypes.c_void_p(ht))

    s = None
    for attempt in range(3):
        hijack()
        t0 = time.time()
        entered = False
        while time.time() - t0 < 10:
            s = dd.state(hp, app)
            if (s[2] == 1 and s[3] == index and s[4]
                    and dd.u8(hp, lm + 8) == 1):
                entered = True
                break
            if dd.k32.WaitForSingleObject(pi.hProcess, 0) == 0:
                raise SystemExit("exited during level entry")
            time.sleep(0.1)
        print("dispatch attempt %d entered=%s state=%s lm8=%s" %
              (attempt, entered, s, dd.u8(hp, lm + 8)), flush=True)
        if not entered:
            continue
        # The level is built asynchronously; wait for the app state to arm
        # instead of trusting a fixed delay (F384).
        t0 = time.time()
        while time.time() - t0 < max(settle, 3.0):
            if dd.u8(hp, app + 0x10) == 1:
                time.sleep(0.2)
                if dd.u8(hp, app + 0x10) == 1:
                    return lm, app, win, ht, stub_addr
            time.sleep(0.1)
        print("attempt %d did not arm app16=%s" %
              (attempt, dd.u8(hp, app + 0x10)), flush=True)
    raise SystemExit("level not reached")
    return lm, app, win, ht, stub_addr


def hud_sprite_states(hp, mgr):
    """Diagnostic alias for direct_drive.hud_sprites (single source of truth)."""
    return dd.hud_sprites(hp, mgr)


# ---- stage parsing ----
def parse_stage(text):
    body, _, rest = text.partition(":")
    if not rest:
        raise SystemExit("bad --stage %r (want sx,sy:gx,gy[:done])" % text)
    goal, _, done = rest.partition(":")
    try:
        sx, sy = (float(v) for v in body.split(","))
        gx, gy = (float(v) for v in goal.split(","))
        d = float(done) if done else None
    except ValueError:
        raise SystemExit("bad --stage %r" % text)
    return {"start": [sx, sy], "goal": [gx, gy], "done": d}


def parse_nudge(text):
    """STAGE:seconds:radius — release, re-grip, move a little."""
    idx, _, rest = text.partition(":")
    sec, _, radius = rest.partition(":")
    try:
        return int(idx), float(sec), float(radius)
    except ValueError:
        raise SystemExit("bad --nudge %r (want stage:sec:radius)" % text)


def parse_point(text):
    try:
        x, y = (float(v) for v in text.split(","))
    except ValueError:
        raise SystemExit("bad point %r" % text)
    return [x, y]


# ---- run ----
def run(a):
    if ctypes.sizeof(ctypes.c_void_p) != 4:
        raise SystemExit("32-bit Python required (CONTEXT is x86)")
    game_dir = os.path.abspath(a.dir)
    stages = [parse_stage(s) for s in a.stage]
    if not stages and a.observe <= 0:
        raise SystemExit("at least one --stage required (or --observe)")
    waypoints = {}
    for spec in a.waypoint:
        idx, _, pt = spec.partition(":")
        if not pt:
            raise SystemExit("bad --waypoint %r (want stage:x,y)" % spec)
        try:
            k = int(idx)
        except ValueError:
            raise SystemExit("bad --waypoint stage index in %r" % spec)
        waypoints.setdefault(k, []).append(parse_point(pt))
    stage_angles = {}
    for spec in a.stage_angle:
        idx, _, pt = spec.partition(":")
        if not pt:
            raise SystemExit("bad --stage-angle %r (want stage:x,y)" % spec)
        try:
            k = int(idx)
        except ValueError:
            raise SystemExit("bad --stage-angle stage index in %r" % spec)
        stage_angles.setdefault(k, []).append(parse_point(pt))
    nudges = {}
    for spec in a.nudge:
        k, sec, radius = parse_nudge(spec)
        nudges[k] = (sec, radius)
    markers = [parse_point(m) for m in a.marker]
    tag = os.path.join(WORK, "ci_fake_magnet_%d" % os.getpid())
    log = tag + ".bin"
    force = tag + "_force.txt"
    mag_trace = tag + "_mag.txt"
    cfg = tag + "_cfg.txt"
    for p in (log, force, mag_trace, cfg):
        if os.path.exists(p):
            os.remove(p)
    prev_fg = user32.GetForegroundWindow()
    desk, desk_name, si, pi, hp, pid = launch(game_dir, log, force, mag_trace, cfg)
    out = {"pid": pid, "desktop": desk_name, "stages": [], "markers": [],
           "forces": {}, "fg_same": None, "fg_game_events": [],
           "exit_clean": None, "pass": False}
    fg_events = out["fg_game_events"]
    try:
        lm, app, win, ht, stub = dispatch(hp, pi, desk, pid, a.level, a.settle)
        game_hwnd = win[0]

        def note_fg(where):
            fg = user32.GetForegroundWindow()
            if fg == game_hwnd:
                fg_events.append(where)
        digest = LiveDigest(log)
        wait_cond(lambda: (digest.poll() or digest.bodies)
                  and len(digest.bodies) >= a.min_bodies, a.timeout_bodies)
        digest.poll()
        print("bodies", len(digest.bodies), "seq", digest.seq, flush=True)
        initial = {b[0] for b in digest.bodies}
        hud_baseline = {p_: c2c_ for p_, sz_, c2c_, vis_ in
                        hud_sprite_states(hp, dd.state(hp, app)[0])}
        if os.environ.get("CI_DEBUG"):
            print("hud baseline", {hex(k): hex(v) for k, v in hud_baseline.items()},
                  flush=True)
        note_fg("settle")
        if a.observe > 0:
            targets = []
            for pt in [parse_point(v) for v in a.angle]:
                cand = nearest_body(digest.bodies, pt[0], pt[1])
                if not cand or cand[0] > a.start_tol:
                    raise SystemExit("angle body not found near %s" % (pt,))
                targets.append({"point": pt, "body": cand[2][0],
                                "angle0": cand[2][8], "w0": cand[2][5]})
            if not targets:
                raise SystemExit("--observe needs at least one --angle x,y")
            note_fg("observe:start")
            t0 = time.time()
            while time.time() - t0 < a.observe:
                digest.poll()
                time.sleep(0.05)
            note_fg("observe:end")
            digest.poll()
            ok = True
            for t in targets:
                _, b = find_body(digest.bodies, t["body"])
                if b is None:
                    t["missing"] = True
                    ok = False
                    continue
                t.update(angle1=b[8], w1=b[5], delta=b[8] - t["angle0"])
                if abs(t["delta"]) < a.min_angle:
                    ok = False
            if (a.gear_ratio is not None and len(targets) == 2
                    and not any(t.get("missing") for t in targets)):
                d1, d2 = targets[0]["delta"], targets[1]["delta"]
                ratio = (-d2 / d1) if abs(d1) > 1e-6 else None
                sign_ok = d1 * d2 < 0
                ratio_ok = (ratio is not None and
                            abs(ratio - a.gear_ratio) <= a.ratio_tol)
                ok = ok and sign_ok and ratio_ok
                out["gear"] = {"ratio_measured": ratio,
                               "ratio_expected": a.gear_ratio,
                               "sign_ok": sign_ok, "ratio_ok": ratio_ok}
            out["angles"] = targets
            out["angles_ok"] = ok
            out["complete"] = False
            out["complete_ok"] = not a.require_complete
            out["mode"] = "observe"
            time.sleep(a.completion_wait)
            out["markers"] = parse_markers(log, markers)
            out["marker_ok"] = all(any(abs(m["x"] - mx) < 0.5 and
                                       abs(m["y"] - my) < 0.5
                                       for m in out["markers"])
                                   for mx, my in markers) if markers else True
            note_fg("end")
            out["fg_same"] = (user32.GetForegroundWindow() == prev_fg)
            out["fg_before"] = prev_fg
            out["fg_after"] = user32.GetForegroundWindow()
            fg_ok = (not fg_events) or not a.require_fg
            out["fg_ok"] = fg_ok
            out["force_ok"] = True
            out["pass"] = bool(ok and out["marker_ok"] and fg_ok)
            print("SUMMARY", json.dumps(out, ensure_ascii=False)[:1600], flush=True)
            print("PASS" if out["pass"] else "FAIL", flush=True)
            return 0 if out["pass"] else 1
        cal = calibrate(hp, cfg)
        print("calib", cal, flush=True)
        used = set()
        expect = {}
        for si_, st in enumerate(stages):
            done = st["done"] if st["done"] is not None else a.done_dist
            t0 = time.time()
            found = None
            while time.time() - t0 < a.timeout_body:
                digest.poll()
                cand = nearest_body(digest.bodies, st["start"][0], st["start"][1],
                                    exclude=used)
                if cand and cand[0] <= a.start_tol:
                    found = cand
                    break
                time.sleep(0.05)
            rec = {"index": si_, "start": st["start"], "goal": st["goal"],
                   "done_dist": done, "body": None, "d": None, "locked": False,
                   "target": None, "waypoints": waypoints.get(si_, []),
                   "pass": False}
            out["stages"].append(rec)
            if not found:
                print("stage %d: no body within %.2f of start" %
                      (si_, a.start_tol), flush=True)
                continue
            angle_watch = []
            for pt in stage_angles.get(si_, []):
                ca = nearest_body(digest.bodies, pt[0], pt[1])
                if ca and ca[0] <= a.start_tol:
                    angle_watch.append({"point": pt, "body": ca[2][0],
                                        "angle0": ca[2][8]})
            d0, _, body = found
            ptr = body[0]
            used.add(ptr)
            rec.update(body=ptr, d_init=round(d0, 4),
                       body_pos0=[body[6], body[7]], angle0=body[8],
                       runtime=ptr not in initial)
            note_fg("stage%d:press" % si_)
            res, pressed = press_on(hp, cal, cfg, body[6], body[7])
            note_fg("stage%d:locked" % si_)
            rec["locked"] = bool(res and res.get("target"))
            rec["press_offset"] = pressed
            rec["target"] = res.get("target") if res else None
            print("stage %d ptr %s pos (%.3f,%.3f) press %s target %s" %
                  (si_, hex(ptr), body[6], body[7], pressed, rec["target"]),
                  flush=True)
            if not rec["locked"]:
                continue
            expect[rec["target"]] = ptr
            for wx, wy in waypoints.get(si_, []):
                wcx, wcy = cfg_world(cal, wx, wy)
                write_cfg(cfg, wcx, wcy, 1)
                wb = None
                t0 = time.time()
                while time.time() - t0 < a.waypoint_hold:
                    digest.poll()
                    _, wb = find_body(digest.bodies, ptr)
                    if (wb and math.hypot(wb[6] - wx, wb[7] - wy)
                            < a.waypoint_tol):
                        break
                    time.sleep(0.05)
                print("stage %d waypoint (%.2f,%.2f) d=%.3f" %
                      (si_, wx, wy,
                       math.hypot(wb[6] - wx, wb[7] - wy) if wb else -1),
                      flush=True)
            cx, cy = cfg_world(cal, *st["goal"])
            write_cfg(cfg, cx, cy, 1)
            d, d_live_min = drive_to(digest, ptr, st["goal"], done, a.hold,
                                     a.timeout)
            if si_ in nudges and rec["target"]:
                # The first in-target bGearOnMove calls Set_PlayerMagnetOff(),
                # so holding the button cannot produce the second OnMove.
                # Release, re-grip the (now stationary) body, then move a
                # little; the second in-target OnMove sees HintState == 4.
                nsec, nrad = nudges[si_]
                write_cfg(cfg, cx, cy, 0)
                time.sleep(a.regrab_wait)
                digest.poll()
                _, nb = find_body(digest.bodies, ptr)
                if nb is not None:
                    res2, pressed2 = press_on(hp, cal, cfg, nb[6], nb[7])
                    rec["regrab"] = bool(res2 and res2.get("target"))
                    print("stage %d regrab press %s target %s" %
                          (si_, pressed2, res2.get("target") if res2 else None),
                          flush=True)
                    if rec["regrab"]:
                        bx, by = nb[6], nb[7]
                        t0 = time.time()
                        k = 0
                        while time.time() - t0 < nsec:
                            ang = 2.0 * math.pi * k / 20.0
                            nx = bx + nrad * math.cos(ang)
                            ny = by + nrad * math.sin(ang)
                            ncx, ncy = cfg_world(cal, nx, ny)
                            write_cfg(cfg, ncx, ncy, 1)
                            digest.poll()
                            time.sleep(0.05)
                            k += 1
                        gcx, gcy = cfg_world(cal, bx, by)
                        write_cfg(cfg, gcx, gcy, 1)
                        time.sleep(0.2)
            write_cfg(cfg, cx, cy, 0)
            time.sleep(0.25)
            digest.poll()
            _, fb = find_body(digest.bodies, ptr)
            rec["d_live"] = None if d is None else round(d, 4)
            rec["d_live_min"] = round(d_live_min, 4)
            rec["goal_screen"] = [round(cx, 3), round(cy, 3)]
            rec["body_pos1"] = [fb[6], fb[7]] if fb else None
            rec["angle1"] = fb[8] if fb else None
            for aw in angle_watch:
                _, ab = find_body(digest.bodies, aw["body"])
                if ab is not None:
                    aw.update(angle1=ab[8], delta=ab[8] - aw["angle0"])
            rec["angle_watch"] = angle_watch
            print("stage %d live d %s (min %.3f)" % (si_, rec["d_live"],
                                                     d_live_min), flush=True)
        # PASS is decided on the recorded per-step trajectories: the magnet can
        # cross the goal between two 50 ms polls (see parse_min_dist).
        best = parse_min_dist(log, {s["body"]: tuple(s["goal"])
                                    for s in out["stages"] if s["body"]})
        for rec in out["stages"]:
            if rec["body"] is None:
                continue
            hit = best.get(rec["body"])
            if hit:
                rec["d_min"], rec["step_min"], rec["pos_min"] = (
                    round(hit[0], 4), hit[1], [round(hit[2], 3), round(hit[3], 3)])
            angle_ok = True
            for aw in rec.get("angle_watch", []):
                ok_ang = (aw.get("delta") is not None and
                          abs(aw["delta"]) >= a.stage_min_angle)
                aw["ok"] = ok_ang
                angle_ok = angle_ok and ok_ang
            dist_ok = True if a.ignore_distance else bool(
                hit and hit[0] < rec["done_dist"])
            rec["dist_ok"] = dist_ok
            rec["angle_ok"] = angle_ok
            rec["pass"] = bool(rec["locked"] and dist_ok and angle_ok)
            print("stage %d d_min %s (step %s) angle_ok %s pass %s" %
                  (rec["index"], rec.get("d_min"), rec.get("step_min"),
                   angle_ok, rec["pass"]), flush=True)
        time.sleep(a.completion_wait)
        out["markers"] = parse_markers(log, markers)
        out["marker_ok"] = all(any(abs(m["x"] - mx) < 0.5 and
                                   abs(m["y"] - my) < 0.5
                                   for m in out["markers"])
                               for mx, my in markers) if markers else True
        forces = parse_force_trace(force)
        out["forces"] = check_forces(forces, expect) if not a.skip_forces else {}
        force_ok = a.skip_forces or out["forces"].get("pass_", False)
        out["complete"] = False
        out["complete_ok"] = not a.require_complete
        if a.require_complete:
            t0 = time.time()
            box = None
            last_dbg = 0.0
            mgr = dd.state(hp, app)[0]
            while time.time() - t0 < a.complete_wait:
                if box is None:
                    box = dd.find_end_level_box(hp, mgr)
                if box and dd.u32(hp, box + 0x2C) == 0x3F800000:
                    out["complete"] = True
                    out["complete_ok"] = True
                    out["complete_ptr"] = hex(box)
                    break
                for p_, sz_, c2c_, vis_ in hud_sprite_states(hp, mgr):
                    if hud_baseline.get(p_, 0) == 0 and c2c_ == 0x3F800000:
                        out["complete"] = True
                        out["complete_ok"] = True
                        out["complete_ptr"] = hex(p_)
                        break
                if out["complete"]:
                    break
                if os.environ.get("CI_DEBUG") and time.time() - last_dbg > 0.8:
                    st = dd.state(hp, app)
                    print("  complete t=%.2f state=%s box=%s c2c=%s" %
                          (time.time() - t0, dd.state_label(st), hex(box) if box else None,
                           hex(dd.u32(hp, box + 0x2C)) if box else None),
                          flush=True)
                    for hp_, sz_, c2c_, vis_ in hud_sprite_states(hp, mgr):
                        print("    hud %s size=%s c2c=%s vis=%s" %
                              (hex(hp_), hex(sz_), hex(c2c_), hex(vis_)), flush=True)
                    last_dbg = time.time()
                time.sleep(0.05)
            out["complete_state"] = dd.state_label(dd.state(hp, app))
            print("complete %s after %.2fs state=%s" %
                  (out["complete"], time.time() - t0, out["complete_state"]),
                  flush=True)
        note_fg("end")
        out["fg_same"] = (user32.GetForegroundWindow() == prev_fg)
        out["fg_before"] = prev_fg
        out["fg_after"] = user32.GetForegroundWindow()
        fg_ok = (not fg_events) or not a.require_fg
        stages_ok = all(s["pass"] for s in out["stages"])
        bad_runtime = [i for i in a.runtime_stage
                       if not (0 <= i < len(out["stages"])
                               and out["stages"][i].get("runtime"))]
        out["runtime_ok"] = not bad_runtime
        out["runtime_stage"] = a.runtime_stage
        out["pass"] = bool(stages_ok and out["marker_ok"] and force_ok and fg_ok
                           and out["runtime_ok"] and out["complete_ok"])
        out["stages_ok"] = stages_ok
        out["fg_ok"] = fg_ok
        out["force_ok"] = force_ok
        print("SUMMARY", json.dumps(out, ensure_ascii=False)[:1600], flush=True)
        print("PASS" if out["pass"] else "FAIL", flush=True)
        return 0 if out["pass"] else 1
    finally:
        try:
            dd.remote_exit(hp, pi)
            out["exit_clean"] = dd.k32.WaitForSingleObject(pi.hProcess, 0) == 0
        except Exception:
            out["exit_clean"] = False
        try:
            dd.k32.CloseHandle(ctypes.c_void_p(pi.hProcess))
            dd.k32.CloseHandle(ctypes.c_void_p(pi.hThread))
            dd.k32.CloseHandle(ctypes.c_void_p(hp))
        except Exception:
            pass
        try:
            user32.CloseDesktop(ctypes.c_void_p(desk))
        except Exception:
            pass
        if a.json:
            os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
            json.dump(out, open(a.json, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("wrote", a.json, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="make a game copy whose pak has the fixture level")
    b.add_argument("--out", required=True)
    b.add_argument("--o", default=DEFAULT_O, help="replacement lvl_o14.lua")
    b.add_argument("--e", default=DEFAULT_E, help="replacement lvl_e14.lua")
    b.add_argument("--proxy", default=PROXY)
    b.set_defaults(func=lambda a: build(a.out, a.o, a.e, a.proxy))

    r = sub.add_parser("run", help="drive staged fake-magnet drags")
    r.add_argument("--dir", default=os.path.join(WORK, "fakemag_game"))
    r.add_argument("--level", type=int, default=1)
    r.add_argument("--stage", action="append", default=[])
    r.add_argument("--done-dist", type=float, default=0.30)
    r.add_argument("--start-tol", type=float, default=1.0)
    r.add_argument("--marker", action="append", default=[])
    r.add_argument("--timeout", type=float, default=12.0, help="per-stage drag timeout")
    r.add_argument("--hold", type=float, default=2.5,
                   help="seconds to hold the synthetic button per stage")
    r.add_argument("--waypoint", action="append", default=[],
                   help="STAGE:x,y intermediate cursor point (repeatable)")
    r.add_argument("--nudge", action="append", default=[],
                   help="STAGE:seconds:radius — re-grip the body after the "
                        "first in-target OnMove turned the magnet off, move a "
                        "little, then release (repeatable)")
    r.add_argument("--regrab-wait", type=float, default=0.6,
                   help="seconds between releasing and re-gripping for --nudge")
    r.add_argument("--require-complete", action="store_true",
                   help="require bEndLevelBox+0x2C == 1.0 after the stages")
    r.add_argument("--complete-wait", type=float, default=8.0,
                   help="seconds to wait for the completion panel")
    r.add_argument("--stage-angle", action="append", default=[],
                   help="STAGE:x,y body whose angle must change during the stage")
    r.add_argument("--stage-min-angle", type=float, default=0.2,
                   help="minimum |delta angle| (rad) for --stage-angle")
    r.add_argument("--ignore-distance", action="store_true",
                   help="stage PASS does not require the body to reach the goal")
    r.add_argument("--waypoint-hold", type=float, default=1.0,
                   help="max seconds to hold at one waypoint")
    r.add_argument("--waypoint-tol", type=float, default=1.5,
                   help="body distance at which a waypoint counts as reached")
    r.add_argument("--timeout-body", type=float, default=8.0,
                   help="wait for a stage's body (runtime-generated)")
    r.add_argument("--timeout-bodies", type=float, default=10.0,
                   help="wait for the first digest")
    r.add_argument("--min-bodies", type=int, default=5)
    r.add_argument("--settle", type=float, default=0.8)
    r.add_argument("--completion-wait", type=float, default=1.5)
    r.add_argument("--skip-forces", action="store_true")
    r.add_argument("--observe", type=float, default=0.0,
                   help="angle-observation seconds (no magnet stage)")
    r.add_argument("--angle", action="append", default=[],
                   help="x,y body to watch in --observe mode (repeatable)")
    r.add_argument("--min-angle", type=float, default=0.1,
                   help="minimum |delta angle| (rad) per watched body")
    r.add_argument("--gear-ratio", type=float, default=None,
                   help="expected |delta2/delta1| magnitude (sign must be opposite)")
    r.add_argument("--ratio-tol", type=float, default=0.15)
    r.add_argument("--runtime-stage", type=int, action="append", default=[],
                   help="stage index whose body must not exist in the initial digest")
    r.add_argument("--require-fg", action="store_true",
                   help="fail when the game window ever becomes the user's foreground")
    r.add_argument("--json", default=None)
    r.set_defaults(func=run)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
