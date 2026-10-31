"""Map level nodes from pak `GuiLvl.txt` to game design coordinates.

Usage:
  python tools/map_nodes.py <GuiLvl.txt> [--csv out.csv]

GuiLvl.txt holds `<GUIelement>` records with `Command`, `PosX`, `PosY`,
`Rotation`. Commands 299..350 are the 52 level buttons in level order;
399..412 are path decorations, 112 is the top-right "Menu" label and 113 the
position marker.

The map view draws a node at design = (PosX, PosY) + MAP_ORIGIN. MAP_ORIGIN was
fitted against 51 icon centers detected in a screenshot (residual std 3.7 px)
and cross-checked with command 112 at design (787,237).

Criteria: 52 rows, level 1 = Command 299. Clicking row 1 at (214,192) loads
the first level (verified, F264). Boundaries: assumed a fixed, unscaled map
view; if the map scrolls/zooms, re-fit MAP_ORIGIN from a fresh screenshot.
"""
import argparse
import re

MAP_ORIGIN = (506.15, 355.5)
LEVEL_CMDS = range(299, 351)


def parse(path):
    t = open(path, "r", encoding="ascii", errors="replace").read()
    els = re.findall(r"<GUIelement>(.*?)</GUIelement>", t, re.S | re.I)
    out = {}
    for e in els:
        d = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', e))
        if "Command" in d and "PosX" in d and "PosY" in d:
            out[int(d["Command"])] = (float(d["PosX"]), float(d["PosY"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guilvl")
    ap.add_argument("--csv", default="")
    a = ap.parse_args()
    nodes = parse(a.guilvl)
    rows = []
    for i, cmd in enumerate(LEVEL_CMDS, 1):
        if cmd not in nodes:
            raise SystemExit("missing command %d" % cmd)
        x, y = nodes[cmd]
        rows.append((i, cmd, x + MAP_ORIGIN[0], y + MAP_ORIGIN[1]))
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            f.write("level,command,design_x,design_y\n")
            for r in rows:
                f.write("%d,%d,%.1f,%.1f\n" % r)
    print("levels", len(rows), "first", rows[0][2:], "last", rows[-1][2:])


if __name__ == "__main__":
    main()
