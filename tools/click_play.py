"""Click a logical point in the game window, compensating two input quirks.

Usage:
  python tools/click_play.py <game_pid> [--x 350] [--y 325] [--hold 150]

Coordinates are game-logical (design box 1018x739). The game maps the real
cursor as `client_coord / scale`, so the click must be sent at
`client_origin + logical * scale`, where `scale = client_width / 1018`.
The button must be held ~150 ms: a instantaneous down/up is missed by the
game's frame-polled mouse state (hover highlight still updates, which is a
cheap way to confirm the position before pressing).

Criteria: with Add_* breakpoints armed via tools/moduledb.py, a successful
click makes level init emit its `#HB` lines; otherwise the screenshot changes
from the menu.
Boundaries: requires a real (SendInput-class) click; WM_*PostMessage is not
enough. Window must be the game's top-level window (>200 px wide, title
contains "Magnetic").
"""
import argparse
import ctypes
import sys
import time

sys.path.insert(0, r"C:/tmp/Magnetic Adventure/tools")
import uistate as us


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int)
    ap.add_argument("--x", type=float, default=350.0, help="logical x (design box)")
    ap.add_argument("--y", type=float, default=325.0, help="logical y (design box)")
    ap.add_argument("--hold", type=int, default=150, help="button hold, ms")
    a = ap.parse_args()

    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    win = us.find_window(a.pid)
    if not win:
        raise SystemExit("game window not found for pid %d" % a.pid)
    ox, oy, w, h = us.client_rect(win)
    scale = w / 1018.0
    x = int(ox + a.x * scale)
    y = int(oy + a.y * scale)
    u = us.u
    u.ShowWindow(win[0], 9)
    u.SetForegroundWindow(win[0])
    time.sleep(0.3)
    u.SetCursorPos(x, y)
    time.sleep(0.2)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(a.hold / 1000.0)
    u.mouse_event(0x0004, 0, 0, 0, 0)
    print("win", win, "client", (ox, oy, w, h), "scale", scale, "click", (x, y))


if __name__ == "__main__":
    main()
