"""Le Petit Sub building plan: three A3 sheets as SVG (1:5, detail 2:1).

Sealed box, 22 mm OSB, glued with biscuits (size 20); front and back are full 340 x 530 plates,
sides between them, top and bottom between the plates and the sides. Two SB26SFCL38-4 in the
sides, flush in a 4.5 mm recess. Every dimension comes from sub.py.

    python tools/make_building_plan.py   ->  docs/plans/building-plan-sheet-{1,2,3}.svg
"""
import math
from pathlib import Path

import sub
from sub import (BIS_PLATE_SIDE, BIS_PLATE_TB, BIS_SIDE_TB, CUTOUT, D, DRIVER, DRV_U, DRV_V, GLAND, H,
                 HOLE_ANGLES, ID, IH, IW, RECESS, RECESS_DEPTH, STRIP, T, TIE, WIN, WIN_TOP, W)

OUT = Path(__file__).resolve().parent.parent / "docs" / "plans"
PW, PH = 420, 297                    # A3 landscape, mm
DATE = "16.10.2026"
REV = "A"
R_REC, R_CUT, R_PCD = RECESS / 2, CUTOUT / 2, DRIVER["pcd"] / 2
INS_DRILL = 6.5
GL_V = H - GLAND["from_bottom"]      # gland centre below the top: 430
WIN_BOT = WIN_TOP + T                # window brace underside: 352
TIE_U = (W / 2 - T / 2, W / 2 + T / 2)    # tie strip across the width, outside coordinates: 159..181

CSS = """
text{font-family:Helvetica,Arial,sans-serif;fill:#000}
.o{stroke:#000;stroke-width:.35;fill:none}.t{stroke:#000;stroke-width:.18;fill:none}
.hd{stroke:#000;stroke-width:.18;fill:none;stroke-dasharray:1.2 .8}
.c{stroke:#000;stroke-width:.13;fill:none;stroke-dasharray:4 .8 .6 .8}
.d{stroke:#000;stroke-width:.13;fill:none}
.cut{stroke:#000;stroke-width:.35;fill:url(#h)}.cutw{stroke:none;fill:#fff}
.bis{fill:#d9b06a;stroke:#5a3e12;stroke-width:.15}
.bish{fill:#f3e6c9;stroke:#5a3e12;stroke-width:.15;stroke-dasharray:.8 .5}
.drv{fill:#8a9097;stroke:#000;stroke-width:.25}.mag{fill:#4a4f55;stroke:#000;stroke-width:.25}
.gk{fill:#2b2b2b;stroke:none}.ins{fill:#c9a74a;stroke:#000;stroke-width:.2}
.wool{fill:#efede6;stroke:#9a958a;stroke-width:.15;stroke-dasharray:.6 .6}
.g{fill:#555}.w{fill:#fff}.ow{stroke:#000;stroke-width:.35;fill:#fff}
.lb{paint-order:stroke;stroke:#fff;stroke-width:.6;stroke-linejoin:round}
.arr{stroke:#b3461f;stroke-width:.5;fill:none}.arrh{fill:#b3461f}
"""
DEFS = """<defs>
<pattern id="h" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<line x1="0" y1="0" x2="0" y2="1.2" stroke="#000" stroke-width=".12"/></pattern>
</defs>"""


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Sheet:
    def __init__(s):
        s.e = []

    def raw(s, x):
        s.e.append(x)

    def line(s, x1, y1, x2, y2, c="t"):
        s.raw(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" class="{c}"/>')

    def rect(s, x, y, w, h, c="o"):
        s.raw(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" class="{c}"/>')

    def circle(s, cx, cy, r, c="o"):
        s.raw(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" class="{c}"/>')

    def poly(s, pts, c="o"):
        s.raw(f'<polygon points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" class="{c}"/>')

    def text(s, x, y, t, size=2.0, anchor="start", rot=0, weight=None, fill=None, cls=None):
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        a += f' class="{cls}"' if cls else ""
        a += f' transform="rotate({rot} {f(x)} {f(y)})"' if rot else ""
        a += f' font-weight="{weight}"' if weight else ""
        a += f' style="fill:{fill}"' if fill else ""
        t = t.replace("&", "&amp;").replace("<", "&lt;")
        s.raw(f'<text x="{f(x)}" y="{f(y)}" font-size="{size}"{a}>{t}</text>')

    def lens(s, cx, cy, L, w, vertical=False, c="bis"):
        """Biscuit symbol: a lens L long, w wide (paper mm)."""
        R = (L * L / 4 + w * w / 4) / w
        d = f"M{f(-L/2)},0 A{f(R)},{f(R)} 0 0 1 {f(L/2)},0 A{f(R)},{f(R)} 0 0 1 {f(-L/2)},0Z"
        rot = " rotate(90)" if vertical else ""
        s.raw(f'<path d="{d}" transform="translate({f(cx)},{f(cy)}){rot}" class="{c}"/>')

    def tick(s, x, y):
        s.line(x - .8, y + .8, x + .8, y - .8, "o")

    def dimh(s, x1, x2, y, label, yref=None, size=1.8):
        s.line(x1 - 1.2, y, x2 + 1.2, y, "d")
        for x in (x1, x2):
            s.tick(x, y)
            if yref is not None:
                s.line(x, yref + (.8 if y > yref else -.8), x, y + (1 if y > yref else -1), "d")
        s.text((x1 + x2) / 2, y - .7, label, size, "middle")

    def dimv(s, y1, y2, x, label, xref=None, size=1.8):
        s.line(x, y1 - 1.2, x, y2 + 1.2, "d")
        for y in (y1, y2):
            s.tick(x, y)
            if xref is not None:
                s.line(xref + (.8 if x > xref else -.8), y, x + (1 if x > xref else -1), y, "d")
        s.text(x - .7, (y1 + y2) / 2, label, size, "middle", rot=-90)

    def leader(s, x1, y1, x2, y2, label, size=1.9, anchor=None):
        s.line(x1, y1, x2, y2, "d")
        s.circle(x1, y1, .25, "g")
        a = anchor or ("start" if x2 >= x1 else "end")
        s.text(x2 + (.8 if a == "start" else -.8), y2 + .6, label, size, a, cls="lb")

    def arrow(s, x1, y1, x2, y2):
        s.line(x1, y1, x2, y2, "arr")
        a = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - 2.2 * math.cos(a) + 1 * math.sin(a), y2 - 2.2 * math.sin(a) - 1 * math.cos(a)),
             (x2 - 2.2 * math.cos(a) - 1 * math.sin(a), y2 - 2.2 * math.sin(a) + 1 * math.cos(a))]
        s.poly(p, "arrh")

    def svg(s, box=None):
        """The whole sheet, or with box = (x, y, w, h) one view of it, for the web pages."""
        x, y, w, h = box or (0, 0, PW, PH)
        size = f'width="{PW}mm" height="{PH}mm" ' if box is None else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" {size}viewBox="{f(x)} {f(y)} {f(w)} {f(h)}">\n'
                f'<style>{CSS}</style>\n{DEFS}\n'
                f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="#fff"/>\n' + "\n".join(s.e)
                + "\n</svg>\n")


class View:
    """Panel coordinates (mm, u right, w down) -> paper at scale k."""

    def __init__(v, sh, ox, oy, k=0.2):
        v.s, v.ox, v.oy, v.k = sh, ox, oy, k

    def p(v, u, w):
        return v.ox + u * v.k, v.oy + w * v.k

    def rect(v, u, w, du, dw, c="o"):
        x, y = v.p(u, w)
        v.s.rect(x, y, du * v.k, dw * v.k, c)

    def cut(v, u, w, du, dw):
        v.rect(u, w, du, dw, "cutw")
        v.rect(u, w, du, dw, "cut")

    def circle(v, u, w, r, c="o"):
        x, y = v.p(u, w)
        v.s.circle(x, y, r * v.k, c)

    def poly(v, pts, c="o"):
        v.s.poly([v.p(u, w) for u, w in pts], c)

    def line(v, u1, w1, u2, w2, c="t"):
        v.s.line(*v.p(u1, w1), *v.p(u2, w2), c)

    def lens(v, u, w, vertical=False, c="bis", L=56, wd=10):
        v.s.lens(*v.p(u, w), L * v.k, wd * v.k, vertical, c)

    def chain_h(v, us, w, off, w_ref=None, labels=None):
        y = v.oy + w * v.k + off
        yref = v.oy + (w if w_ref is None else w_ref) * v.k
        for i in range(len(us) - 1):
            lab = labels[i] if labels else f(us[i + 1] - us[i])
            v.s.dimh(v.ox + us[i] * v.k, v.ox + us[i + 1] * v.k, y, lab, yref)

    def chain_v(v, ws, u, off, u_ref=None, labels=None):
        x = v.ox + u * v.k + off
        xref = v.ox + (u if u_ref is None else u_ref) * v.k
        for i in range(len(ws) - 1):
            lab = labels[i] if labels else f(ws[i + 1] - ws[i])
            v.s.dimv(v.oy + ws[i] * v.k, v.oy + ws[i + 1] * v.k, x, lab, xref)

    def text(v, u, w, t, size=2.0, anchor="start", rot=0, fill=None):
        v.s.text(*v.p(u, w), t, size, anchor, rot, fill=fill)

    def leader(v, u1, w1, x2, y2, label, size=1.85, anchor=None):
        v.s.leader(*v.p(u1, w1), x2, y2, label, size, anchor)


def frame(s, title, scale, n):
    s.rect(10, 10, 400, 277, "o")
    x0, y0 = 283, 252
    s.rect(x0, y0, 127, 35, "o")
    s.text(x0 + 3, y0 + 8.5, "Le Petit Sub", 5.5)
    s.text(x0 + 52, y0 + 8.5, "Le Petit's bigger twin", 2.4)
    s.text(x0 + 3, y0 + 13.5, f"sealed, ≈ 40 l net · 2 × {sub.DRIVER_NAME}, opposed · companion to Le Petit", 1.8)
    s.text(x0 + 3, y0 + 17.5, "22 mm OSB · biscuits (size 20) + wood glue · glued shut, drivers from outside", 1.8)
    s.text(x0 + 3, y0 + 23, title, 2.5)
    s.line(x0, y0 + 25, x0 + 127, y0 + 25, "t")
    s.line(x0 + 72, y0 + 25, x0 + 72, y0 + 35, "t")
    s.line(x0 + 102, y0 + 25, x0 + 102, y0 + 35, "t")
    s.text(x0 + 3, y0 + 29.5, "All dimensions in mm", 1.7)
    s.text(x0 + 3, y0 + 33, f"Rev. {REV} · {DATE}", 1.7)
    s.text(x0 + 75, y0 + 31, scale, 1.7)
    s.text(x0 + 105, y0 + 31, f"Sheet {n} / 3", 1.7)


def heading(s, x, y, t, sub_=None):
    s.text(x, y, t, 3.0)
    if sub_:
        s.text(x, y + 4.5, sub_, 1.8, fill="#333")


def legend(s, x, y):
    s.text(x, y, "LEGEND", 2.4)
    s.lens(x + 4, y + 5, 11.2, 2.4)
    s.text(x + 11, y + 5.7, "biscuit slot, size 20 (56 × 23 × 4), centred in the 22 mm edge", 1.8)
    s.lens(x + 4, y + 10, 11.2, 2.4, c="bish")
    s.text(x + 11, y + 10.7, "biscuit slot, hidden (other face)", 1.8)
    s.rect(x + 1, y + 13.5, 6, 3, "cut")
    s.text(x + 11, y + 15.7, "cut section, OSB", 1.8)
    s.rect(x + 1, y + 18.5, 6, 3, "hd")
    s.text(x + 11, y + 20.7, "hidden edge / glue line of a brace", 1.8)


def notes(s, x, y, title, lines, size=1.85, step=3.6):
    s.text(x, y, title, 2.6)
    for i, t in enumerate(lines):
        s.text(x, y + 5 + i * step, t, size)
    return y + 5 + len(lines) * step


def drv_holes(v, uc, wc, c="o"):
    """Recess, cutout, bolt circle and the six insert holes, seen on the outside face."""
    v.circle(uc, wc, R_REC)
    v.circle(uc, wc, R_CUT)
    v.circle(uc, wc, R_PCD, "c")
    for a in HOLE_ANGLES:
        u = uc + R_PCD * math.cos(math.radians(a))
        w = wc - R_PCD * math.sin(math.radians(a))
        v.circle(u, w, INS_DRILL / 2, c)
    v.line(uc - R_REC - 12, wc, uc + R_REC + 12, wc, "c")
    v.line(uc, wc - R_REC - 12, uc, wc + R_REC + 12, "c")


def driver_section(v, side, wc):
    """Schematic SB26SFCL38-4 in section, mounted in a side panel. side: -1 left (outside at u=0),
    +1 right (outside at u=W). Depths along u from the datasheet: flange 3.56, 116.8 behind it."""
    def U(d):                         # depth from the outside face -> u
        return d if side < 0 else W - d
    fl0, fl1 = RECESS_DEPTH - 1 - DRIVER["flange"], RECESS_DEPTH - 1
    back = RECESS_DEPTH + DRIVER["depth"]
    rb, rm, ro = DRIVER["basket"] / 2, DRIVER["magnet"] / 2, DRIVER["od"] / 2
    mg = back - 34                    # front of the magnet
    for sg in (-1, 1):                # basket struts, frame to magnet
        v.poly([(U(fl1), wc + sg * rb), (U(fl1), wc + sg * (rb - 6)), (U(mg), wc + sg * 30),
                (U(mg), wc + sg * 36)], "drv")
    v.poly([(U(fl0), wc - ro), (U(fl1), wc - ro), (U(fl1), wc - rb + 4), (U(fl0), wc - rb + 4)], "drv")
    v.poly([(U(fl0), wc + ro), (U(fl1), wc + ro), (U(fl1), wc + rb - 4), (U(fl0), wc + rb - 4)], "drv")
    v.poly([(U(mg), wc - rm), (U(back), wc - rm), (U(back), wc + rm), (U(mg), wc + rm)], "mag")
    # cone from the surround to the voice coil, surround roll and dust cap just proud of the face
    v.poly([(U(fl0), wc - 103), (U(fl0), wc + 103), (U(55), wc + 20), (U(55), wc - 20)], "ow")
    for sg in (-1, 1):
        c = wc + sg * 108.5
        v.poly([(U(fl0 - 5.5 * math.sin(t)), c + 5.5 * math.cos(t)) for t in
                [i * math.pi / 12 for i in range(13)]], "ow")
    v.poly([(U(55 - 9 * math.sin(t)), wc + 20 * math.cos(t)) for t in
            [i * math.pi / 16 for i in range(17)]], "ow")


# ---------------------------------------------------------------- sheet 1
def sheet1():
    s = Sheet()
    # FRONT VIEW
    heading(s, 22, 30, "FRONT VIEW", "plain plate, no holes")
    v = View(s, 24, 42)
    v.rect(0, 0, W, H)
    v.rect(T, T, IW, IH, "hd")
    v.rect(T, WIN_TOP, IW, T, "hd")
    v.rect(TIE_U[0], TIE["top"], T, TIE["bottom"] - TIE["top"], "hd")
    for y in BIS_PLATE_SIDE:
        v.lens(T / 2, y, True, "bish")
        v.lens(W - T / 2, y, True, "bish")
    for x in BIS_PLATE_TB:
        v.lens(x, T / 2, c="bish")
        v.lens(x, H - T / 2, c="bish")
    v.line(W / 2, -10, W / 2, H + 10, "c")
    for u in (-14, W + 14):          # section A-A: horizontal, at driver height
        x, y = v.p(u, DRV_V)
        s.text(x, y + 4, "A", 2.2, "middle")
        s.line(x, y - 1.5, x, y + 1.5, "o")
    for w in (-14, H + 18):          # section B-B: vertical, on the centre line
        x, y = v.p(W / 2, w)
        s.text(x - 2, y + .7, "B", 2.2, "end")
    v.chain_v([0, H], W, 8)
    v.chain_h([0, W], H, 9)

    # LEFT SIDE VIEW (u = 0 at the back, front on the right)
    heading(s, 112, 30, "LEFT SIDE", "front on the right · driver holes: sheet 2, detail C")
    v = View(s, 114, 42)
    v.rect(0, 0, D, H)
    v.line(T, 0, T, H)
    v.line(D - T, 0, D - T, H)
    v.line(T, T, D - T, T, "hd")
    v.line(T, H - T, D - T, H - T, "hd")
    v.rect(T, WIN_TOP, ID, T, "hd")
    drv_holes(v, T + DRV_U, DRV_V)
    v.chain_v([0, DRV_V, H], D, 6)
    v.chain_v([0, H], D, 12)
    v.chain_h([0, T, T + DRV_U, D - T, D], H, 6)
    v.chain_h([0, D], H, 12)
    v.text(D - 4, H - 8, "front", 1.6, "end", fill="#555")

    # SECTION B-B: centre plane, looking at the left side; back on the left, front on the right
    heading(s, 212, 30, "SECTION B–B", "centre plane · front on the right")
    v = View(s, 214, 42)
    v.rect(T, T, ID, IH, "w")
    v.rect(T, WIN_BOT + 8, ID, H - T - WIN_BOT - 8, "wool")
    v.circle(T + DRV_U, DRV_V, DRIVER["basket"] / 2, "t")        # left driver beyond, seen from inside
    v.circle(T + DRV_U, DRV_V, DRIVER["magnet"] / 2, "t")
    v.rect(T + STRIP, WIN_TOP, ID - 2 * STRIP, T, "t")           # side member of the window brace, beyond
    v.cut(0, 0, T, H)
    v.cut(D - T, 0, T, H)
    v.cut(T, 0, ID, T)
    v.cut(T, H - T, ID, T)
    v.cut(T, TIE["top"], ID, TIE["bottom"] - TIE["top"])
    v.cut(T, WIN_TOP, STRIP, T)
    v.cut(D - T - STRIP, WIN_TOP, STRIP, T)
    v.rect(-7, GL_V - 8, T + 13, 16, "g")
    v.text(T + ID / 2, WIN_BOT + 70, "loose wool fill", 1.6, "middle", fill="#555")
    v.text(T + ID / 2, WIN_BOT + 90, "300–500 g", 1.6, "middle", fill="#555")
    v.chain_v([0, TIE["top"], TIE["bottom"], WIN_TOP, WIN_BOT, H], D, 6)
    v.chain_v([0, H], D, 12)
    v.chain_v([GL_V, H], 0, -6, labels=[f(H - GL_V)])
    v.chain_h([0, T, D - T, D], H, 6)
    v.chain_h([0, D], H, 12)
    def lab(u, w, t):
        v.text(u, w, t, 1.6, "middle", fill="#333")
    lab(T + ID / 2, TIE["top"] - 8, "tie strip (cut)")
    lab(T + ID / 2, WIN_TOP - 8, "window brace")
    lab(T + DRV_U, TIE["bottom"] + 45, "left driver, beyond")
    v.text(T + 6, GL_V - 14, f"{sub.GLAND_SIZE} gland", 1.6, fill="#333")

    # VIEW FROM BEHIND
    heading(s, 314, 30, "VIEW FROM BEHIND")
    v = View(s, 316, 42)
    v.rect(0, 0, W, H)
    v.rect(T, T, IW, IH, "hd")
    v.circle(W / 2, GL_V, GLAND["hole"] / 2)
    v.circle(W / 2, GL_V, 14, "t")
    v.line(W / 2, -10, W / 2, H + 10, "c")
    v.line(W / 2 - 25, GL_V, W / 2 + 25, GL_V, "c")
    v.chain_v([0, GL_V, H], W, 6)
    v.chain_v([0, H], W, 12)
    v.chain_h([0, W / 2, W], H, 6)
    v.chain_h([0, W], H, 12)
    v.leader(W / 2 + 8, GL_V - 8, 346, 112, f"{sub.GLAND_SIZE} cable gland, Ø{GLAND['hole']}", 1.7)

    # SECTION A-A: driver height, seen from above, front at the bottom
    heading(s, 22, 176, "SECTION A–A", "at driver height · front at the bottom · the two pushes cancel")
    v = View(s, 24, 188)
    v.rect(T, T, IW, ID, "w")
    wc = T + DRV_U
    for side, u0 in ((-1, 0), (1, W - T)):
        # side panel around the hole: full thickness outside the recess, thinned under it
        def seg(a, b, inner):
            uu = u0 + (RECESS_DEPTH if side < 0 else 0) if inner else u0
            v.cut(uu, a, T - (RECESS_DEPTH if inner else 0), b - a)
        seg(T, wc - R_REC, False)
        seg(wc - R_REC, wc - R_CUT, True)
        seg(wc + R_CUT, wc + R_REC, True)
        seg(wc + R_REC, D - T, False)
        driver_section(v, side, wc)
    v.cut(0, 0, W, T)
    v.cut(0, D - T, W, T)
    v.cut(TIE_U[0], T, T, ID)
    back = RECESS_DEPTH + DRIVER["depth"]
    gap = TIE_U[0] - back
    s.dimh(*(v.p(back, 0)[0], v.p(TIE_U[0], 0)[0]), v.p(0, wc - 70)[1], f"{gap:.0f}")
    s.dimh(*(v.p(TIE_U[1], 0)[0], v.p(W - back, 0)[0]), v.p(0, wc - 70)[1], f"{gap:.0f}")
    for u in (-28, W + 4):
        x, y = v.p(u, wc)
        s.arrow(x + (5 if u < 0 else 0), y, x + (0 if u < 0 else 5), y)
    v.text(-14, wc - 14, "cone out", 1.6, "middle", fill="#b3461f")
    v.text(W + 14, wc - 14, "cone out", 1.6, "middle", fill="#b3461f")
    v.chain_h([0, T, W - T, W], D, 6)
    v.chain_h([0, W], D, 12)
    v.chain_v([0, T, D - T, D], W, 6 + 8)
    v.chain_v([0, D], W, 12 + 8)
    v.leader(W / 2, D - 60, 110, 236, "tie strip 22 × 40", 1.7)
    v.leader(W - back + 12, wc + 50, 110, 243, "magnet Ø120", 1.7)

    # DETAIL C, 2:1: section through the side panel at the frame (u = radius from the driver axis,
    # w = depth from the outside face)
    heading(s, 150, 176, "DETAIL C", "2:1 — driver flush in the side panel")
    v = View(s, 152 - 98 * 2, 200, 2.0)
    r0, r1 = 100, 146
    v.poly([(R_CUT, RECESS_DEPTH), (R_REC, RECESS_DEPTH), (R_REC, 0), (r1, 0), (r1, T), (R_CUT, T)], "cutw")
    v.poly([(R_CUT, RECESS_DEPTH), (R_REC, RECESS_DEPTH), (R_REC, 0), (r1, 0), (r1, T), (R_CUT, T)], "cut")
    v.line(r1, -2, r1, T + 2, "c")
    fl1 = RECESS_DEPTH - 1
    fl0 = fl1 - DRIVER["flange"]
    v.rect(DRIVER["basket"] / 2, fl1, DRIVER["od"] / 2 - DRIVER["basket"] / 2 - 1, 1, "gk")
    v.rect(DRIVER["basket"] / 2, fl0, DRIVER["od"] / 2 - DRIVER["basket"] / 2, DRIVER["flange"], "drv")
    v.poly([(DRIVER["basket"] / 2, fl1), (DRIVER["basket"] / 2 + 2.5, fl1), (r0 + 6.5, T + 6), (r0 + 4, T + 6)], "drv")
    rr = 5.5
    cx = DRIVER["basket"] / 2 - rr - 0.5
    v.poly([(cx + rr * math.cos(t), fl0 - rr * math.sin(t)) for t in [i * math.pi / 16 for i in range(17)]], "ow")
    v.line(cx - rr, fl0, r0, fl0 + 3, "o")
    v.rect(R_PCD - 4, RECESS_DEPTH, 8, 12, "ins")
    v.rect(R_PCD - 2.5, fl0 - 2.8, 5, 2.8, "ow")
    v.rect(R_PCD - 1.25, fl0, 2.5, 16, "ow")
    v.line(R_PCD, fl0 - 5, R_PCD, RECESS_DEPTH + 16, "c")
    v.chain_v([0, RECESS_DEPTH, T], r1, 5)
    v.chain_v([fl0, fl1], DRIVER["basket"] / 2, -5, labels=["3.56"])
    lx = 256
    for (u, w), t, y in (((R_PCD, fl0 - 2), "M5 × 16 pan head", 196),
                         ((DRIVER["basket"] / 2 + 6, fl0 + 1.5), "frame, 3.56 (datasheet)", 202),
                         ((R_REC - 0.5, 2), f"recess Ø{RECESS} × {RECESS_DEPTH}", 208),
                         ((DRIVER["basket"] / 2 + 8, fl1 + .5), "gasket tape, ≈ 1 compressed", 214),
                         ((R_PCD + 2, RECESS_DEPTH + 8), "M5 insert, drill Ø6.5 × 13", 220),
                         ((r1 - 4, 16), "side, OSB 22", 226),
                         ((R_CUT + 1, T - 2), f"cutout Ø{CUTOUT} (basket Ø228.9)", 232)):
        v.s.leader(*v.p(u, w), lx, y + 5, t, 1.75)
    v.text(r0 - 1, fl0 - 2, "surround + cone", 1.5, "end", fill="#555")

    y = notes(s, 300, 176, "NOTES", (
        f"Inside clear {IW} × {IH} × {ID} = {sub.volumes()['gross']:.1f} l gross,",
        f"≈ {sub.volumes()['net']:.0f} l net (braces {sub.volumes()['braces']:.1f} l, drivers ≈ 1.5 l each).",
        "Front and back: full 340 × 530 plates. Sides between them,",
        "top and bottom between plates and sides. Glued shut.",
        "Biscuits size 20 + wood glue, no screws (sheet 2).",
        "Airtight: lacquer inside twice, acrylic bead in every corner.",
        f"Driver flush: frame {DRIVER['flange']} + gasket in a {RECESS_DEPTH} recess.",
        "Check Ø, pcd and frame on the delivered drivers first.",
        "Both drivers + to +: the mirrored mounting moves the cones",
        "out together, so the forces on the box cancel.",
    ), 1.8, 3.4)
    legend(s, 300, y + 3)
    frame(s, "Views and sections", "1:5 (C 2:1) @ A3", 1)
    return s


# ---------------------------------------------------------------- sheet 2
def sheet2():
    s = Sheet()
    heading(s, 22, 28, "FRONT / BACK PLATE", "530 × 340 × 22 · 2 · inner face · 18 slots each")
    v = View(s, 34, 46)
    v.rect(0, 0, W, H)
    for y in BIS_PLATE_SIDE:
        v.lens(T / 2, y, True)
        v.lens(W - T / 2, y, True)
    for x in BIS_PLATE_TB:
        v.lens(x, T / 2)
        v.lens(x, H - T / 2)
    v.rect(TIE_U[0], TIE["top"], T, TIE["bottom"] - TIE["top"], "hd")
    v.rect(T, WIN_TOP, IW, T, "hd")
    v.circle(W / 2, GL_V, GLAND["hole"] / 2)
    v.line(W / 2, -8, W / 2, H + 8, "c")
    v.chain_v([0, *BIS_PLATE_SIDE, H], 0, -6)
    v.chain_h([0, *BIS_PLATE_TB, W], 0, -5)
    v.chain_v([0, TIE["top"], TIE["bottom"], WIN_TOP, WIN_BOT, H], W, 6)
    v.chain_v([GL_V, H], W, 12, labels=[f(H - GL_V)])
    v.chain_v([0, H], W, 18)
    v.chain_h([0, TIE_U[0], TIE_U[1], W], H, 6)
    v.chain_h([0, W], H, 12)
    v.text(TIE_U[0] - 8, TIE["top"] + 25, "tie strip, glued", 1.6, "end", fill="#333")
    v.text(W / 2, WIN_TOP - 10, "window brace, glued", 1.6, "middle", fill="#333")
    v.text(W / 2 - 16, GL_V + 4, f"back only: Ø{GLAND['hole']} gland", 1.6, "end", fill="#333")
    v.text(W / 2, 470, "slots 11 from the edge", 1.5, "middle", fill="#555")

    heading(s, 122, 28, "SIDE", f"530 × {ID} × 22 · 2 · outer face · both the same")
    v = View(s, 132, 46)
    v.rect(0, 0, ID, H)
    drv_holes(v, DRV_U, DRV_V)
    for y in BIS_PLATE_SIDE:
        v.lens(0, y, True)
        v.lens(ID, y, True)
    for x in BIS_SIDE_TB:
        v.lens(x, T / 2, c="bish")
        v.lens(x, H - T / 2, c="bish")
    v.rect(0, WIN_TOP, ID, T, "hd")
    v.chain_v([0, DRV_V, WIN_TOP, WIN_BOT, H], ID, 6)
    v.chain_v([0, H], ID, 12)
    v.chain_h([0, DRV_U, ID], H, 6)
    v.chain_h([0, ID], H, 12)
    v.chain_h([0, *BIS_SIDE_TB, ID], 0, -5)
    v.text(DRV_U, DRV_V + 20, "holes: hole pattern", 1.5, "middle", fill="#555")
    v.text(DRV_U, 470, "slots in both 530 edges", 1.5, "middle", fill="#555")

    heading(s, 210, 28, "TOP / BOTTOM", f"{ID} × {IW} × 22 · 2 · front edge at the bottom")
    v = View(s, 214, 46)
    v.rect(0, 0, IW, ID)
    for x in BIS_PLATE_TB:
        v.lens(x - T, 0)
        v.lens(x - T, ID)
    for y in BIS_SIDE_TB:
        v.lens(0, y, True)
        v.lens(IW, y, True)
    v.text(IW / 2, ID - 18, "front edge", 1.6, "middle", fill="#555")
    v.text(IW / 2, ID / 2, "slots in all four edges", 1.6, "middle", fill="#555")
    v.chain_h([0, *(x - T for x in BIS_PLATE_TB), IW], ID, 6)
    v.chain_h([0, IW], ID, 12)
    v.chain_v([0, *BIS_SIDE_TB, ID], IW, 6)
    v.chain_v([0, ID], IW, 12)

    heading(s, 210, 140, "TIE STRIP", f"{TIE['length']} × {STRIP} × 22 · 1 · on edge")
    v = View(s, 214, 152)
    v.rect(0, 0, TIE["length"], STRIP)
    v.chain_h([0, TIE["length"]], STRIP, 5)
    v.chain_v([0, STRIP], TIE["length"], 5)

    heading(s, 22, 178, "WINDOW BRACE", "4 strips 40 × 22, laid flat · plan view, front at the bottom")
    v = View(s, 34, 194)
    for r in ((0, 0, IW, STRIP), (0, ID - STRIP, IW, STRIP), (0, STRIP, STRIP, WIN["side"]),
              (IW - STRIP, STRIP, STRIP, WIN["side"])):
        v.rect(*r)
    v.rect(TIE_U[0] - T, STRIP + 20, T, ID - 2 * STRIP - 40, "hd")
    v.text(IW / 4 + 10, ID / 2 + 4, "open", 1.6, "middle", fill="#555")
    v.chain_h([0, STRIP, IW - STRIP, IW], ID, 6)
    v.chain_h([0, IW], ID, 12)
    v.chain_v([0, STRIP, ID - STRIP, ID], IW, 6)
    v.chain_v([0, ID], IW, 12)
    v.leader(IW - 60, STRIP / 2, 106, 199, f"front/back members {WIN['fb']}", 1.7)
    v.leader(IW - STRIP / 2, ID / 2 + 40, 106, 214, f"side members {WIN['side']}", 1.7)
    v.leader(TIE_U[0] - T + 5, ID - STRIP - 30, 106, 229, "tie strip above (hidden)", 1.7)
    v.text(-14, ID + 72, f"top face {WIN_TOP} below the box top, glued to all four walls", 1.7)

    heading(s, 150, 205, "DRIVER HOLE PATTERN", "side panels, outer face, 1:5")
    v = View(s, 150 + 34, 218 + 30, 0.2)
    drv_holes(v, 0, 0)
    v.leader(-R_REC * .72, -R_REC * .69, 222, 222, f"recess Ø{RECESS} × {RECESS_DEPTH} deep", 1.7)
    v.leader(-R_CUT * .5, R_CUT * .866, 222, 271, f"cutout Ø{CUTOUT} through", 1.7)
    v.leader(R_PCD * .5, R_PCD * .866, 222, 264, f"6 × Ø{INS_DRILL} × 13 for M5 inserts, on Ø{R_PCD * 2:.0f}", 1.7)
    for i, t in enumerate(("As on the datasheet: holes at 3 and 9 o'clock,", "the others in 60° steps.",
                           "Both sides identical: centre 153 from either", "edge, 175 below the top.")):
        s.text(222, 236 + i * 3.4, t, 1.75, fill="#333")
    for a in (0, 60, 120):
        x, y = v.p(R_PCD * math.cos(math.radians(a)), -R_PCD * math.sin(math.radians(a)))
        s.text(x + (2 if a < 90 else -2), y - 1.2, f"{a}°", 1.5, "start" if a < 90 else "end", fill="#555")

    # tables
    x, y = 290, 28
    s.text(x, y, "CUT LIST", 3.0)
    cols = (0, 36, 80, 92)
    rows = (("Part", "Size (mm)", "Qty", "Note"),
            ("Front plate", "530 × 340 × 22", "1", "plain"),
            ("Back plate", "530 × 340 × 22", "1", "gland"),
            ("Side", f"530 × {ID} × 22", "2", "driver"),
            ("Top / bottom", f"{ID} × {IW} × 22", "2", ""),
            ("Tie strip", f"{TIE['length']} × 40 × 22", "1", "on edge"),
            ("Window, f/b", f"{WIN['fb']} × 40 × 22", "2", "flat"),
            ("Window, side", f"{WIN['side']} × 40 × 22", "2", "flat"),
            ("Biscuits", "size 20", "48", ""))
    for i, row in enumerate(rows):
        yy = y + 7 + i * 4.6
        for c, t in zip(cols, row):
            s.text(x + c, yy, t, 1.9)
        s.line(x, yy + 1.5, x + 116, yy + 1.5, "o" if i == 0 else "t")
    s.text(x, y + 52, "All from one 2000 × 1000 board (cutting plan in the build guide).", 1.8)
    s.text(x, y + 55.5, "Measure the OSB: inside sizes are 340 − 2 × thickness etc.", 1.8)

    y = 96
    s.text(x, y, "HOLES", 3.0)
    for i, row in enumerate((("Recess", f"Ø{RECESS} × {RECESS_DEPTH}", "sides, outside, centre 153 / 175"),
                             ("Cutout", f"Ø{CUTOUT}", "sides, through, same centre"),
                             ("Inserts", "6 × Ø6.5 × 13", f"sides, on Ø{R_PCD * 2:.0f}, M5"),
                             ("Gland", f"Ø{GLAND['hole']}", f"back, centred, {GLAND['from_bottom']:.0f} up"))):
        for c, t in zip((0, 18, 44), row):
            s.text(x + c, y + 7 + i * 4.2, t, 1.9)
    s.text(x, y + 26, "Order: recess (router + circle jig), inserts, then the cutout.", 1.8)
    s.text(x, y + 29.5, "Rout a test recess in scrap and drop a driver in first.", 1.8)

    y = 136
    s.text(x, y, "JOINTS — BISCUITS + GLUE", 3.0)
    for i, t in enumerate((
        "Size 20 (56 × 23 × 4), slots centred in the 22 mm thickness.",
        "Plates onto sides: 6 per 530 edge at 45 / 133 / 221 / 309 / 397 / 485.",
        "Plates onto top/bottom: 3 per edge at 70 / 170 / 270 from the plate",
        "edge (= 48 / 148 / 248 on the top/bottom).",
        "Sides onto top/bottom ends: 3 per edge at 50 / 153 / 256.",
        "18 per plate + 12 sides/top/bottom = 48 biscuits.",
        "Recess edge is 20 mm from the side's edges: the 530-edge slots",
        "are clear of it, the recess is only 4.5 deep.",
        "OSB: reference the joiner from the face, not the fence; check",
        "every slot for voids. No lacquer on glue faces or in the slots.",
        "Braces: glue only, clamped; they are short and fully supported.",
    )):
        s.text(x, y + 6 + i * 3.7, t, 1.82)
    legend(s, x, 226)
    frame(s, "Panels and cut list", "1:5 @ A3", 2)
    return s


# ---------------------------------------------------------------- sheet 3
C, S = 0.5 * math.cos(math.radians(30)), 0.5 * math.sin(math.radians(30))


def P(X, Y, Z):
    """Cabinet oblique: X right, Y up, Z into the box (front at Z = 0); returns (x, y-down)."""
    return X + Z * C, -(Y + Z * S)


def sheet3():
    parts = []

    def box(x0, y0, z0, x1, y1, z1, d=(0, 0, 0), extra=None):
        dx, dy, dz = d
        x0, x1, y0, y1, z0, z1 = x0 + dx, x1 + dx, y0 + dy, y1 + dy, z0 + dz, z1 + dz
        faces = [[(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
                 [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                 [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)]]
        key = (z0 + z1) / 2 - C * 2 * (x0 + x1) / 2 - S * 2 * (y0 + y1) / 2
        parts.append((key, faces, extra or {}, (dx, dy, dz)))

    def slot(c, a, b, L=56, w=6):
        return [tuple(c[i] + sa * a[i] * L / 2 + sb * b[i] * w / 2 for i in range(3))
                for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    ex = 210
    Yd = H - DRV_V                                    # driver centre, Y up
    Zd = T + DRV_U
    yw0, yw1 = H - WIN_BOT, H - WIN_TOP              # window brace, Y up
    yt0, yt1 = H - TIE["bottom"], H - TIE["top"]
    back_slots = [slot((T / 2, y, D - T), Y, X) for y in (H - b for b in BIS_PLATE_SIDE)] + \
                 [slot((W - T / 2, y, D - T), Y, X) for y in (H - b for b in BIS_PLATE_SIDE)] + \
                 [slot((x, T / 2, D - T), X, Y) for x in BIS_PLATE_TB] + \
                 [slot((x, H - T / 2, D - T), X, Y) for x in BIS_PLATE_TB]
    lside_slots = [slot((T, yy, T + z), Z, Y) for z in BIS_SIDE_TB for yy in (T / 2, H - T / 2)]
    box(T, 0, T, W - T, T, D - T, (0, -ex + 40, 0), {"label": "bottom", "face": 1})
    box(0, 0, T, T, H, D - T, (-ex, 0, 0), {"slots": lside_slots, "label": "side", "face": 2})
    box(0, 0, D - T, W, H, D, (0, 0, 2.2 * ex), {"slots": back_slots, "label": "back plate"})
    box(T, yw0, T, W - T, yw1, T + STRIP, extra={"label": "window brace"})
    box(T, yw0, D - T - STRIP, W - T, yw1, D - T)
    box(T, yw0, T + STRIP, T + STRIP, yw1, D - T - STRIP)
    box(W - T - STRIP, yw0, T + STRIP, W - T, yw1, D - T - STRIP)
    box(TIE_U[0], yt0, T, TIE_U[1], yt1, D - T, extra={"label": "tie strip", "face": 1})
    box(T, H - T, T, W - T, H, D - T, (0, ex - 40, 0), {"label": "top", "face": 1})
    box(W - T, 0, T, W, H, D - T, (ex, 0, 0), {"ring": (Yd, Zd), "label": "side", "face": 2})
    box(0, 0, 0, W, H, T, (0, -H - 0.9 * ex, -0.5 * ex), {"label": "front plate"})
    parts.sort(key=lambda p: -p[0])

    s = Sheet()
    heading(s, 20, 28, "EXPLODED VIEW")
    pts = [P(*q) for _, faces, _, _ in parts for fc in faces for q in fc]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    k = min(185 / (max(xs) - min(xs)), 222 / (max(ys) - min(ys)))
    ox = 20 + (185 - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = 38 - k * min(ys)

    def T_(q):
        x, y = P(*q)
        return ox + k * x, oy + k * y

    def ring(xc, yc, zc, r):
        return [T_((xc, yc + r * math.sin(a), zc + r * math.cos(a))) for a in
                [i * 2 * math.pi / 72 for i in range(72)]]

    for _, faces, extra, d in parts:
        for fc in faces:
            s.poly([T_(q) for q in fc], "ow")
        for sl in extra.get("slots", []):
            s.poly([T_(tuple(q[i] + d[i] for i in range(3))) for q in sl], "bis")
        if "ring" in extra:
            yc, zc = extra["ring"]
            xf = W + d[0]
            s.poly(ring(xf, yc, zc, R_REC), "o")
            s.poly(ring(xf, yc, zc, R_CUT), "o")
            for a in HOLE_ANGLES:
                cy = yc + R_PCD * math.sin(math.radians(a))
                cz = zc + R_PCD * math.cos(math.radians(a))
                s.poly(ring(xf, cy, cz, 5), "t")
    for _, faces, extra, d in parts:
        if "label" in extra:
            fc = faces[extra.get("face", 0)]
            cx = sum(T_(q)[0] for q in fc) / 4
            cy = sum(T_(q)[1] for q in fc) / 4
            s.text(cx, cy + 0.8, extra["label"], 2.0, "middle", cls="lb")
    s.text(20, 268, "Not to scale. Front plate pulled down and forward, back plate back, sides, top and bottom out; braces in "
           "place. Biscuit slots shown on the visible faces.", 1.7, fill="#555")

    x, y = 215, 28
    s.text(x, y, "ASSEMBLY", 3.0)
    steps = (
        ("Cut and check.", "All panels from one board (cutting plan). Measure the OSB first; check the plates'",
         "diagonals — they set the box square."),
        ("Driver holes.", "Recess Ø267 × 4.5 with a router and circle jig (test in scrap with a driver),",
         "M5 inserts on Ø250, then the Ø231 cutout. Ø20.5 gland hole in the back."),
        ("Seal.", "Two coats of thinned lacquer on the inside faces. Mask the glue faces and slots."),
        ("Biscuit slots.", "48, size 20 (sheet 2). Reference from the face; check every slot for voids."),
        ("Open box.", "Front plate face down; glue sides, top and bottom onto it with biscuits,",
         "strap-clamped. Dry-fit the back to hold it square."),
        ("Braces.", "Window brace flat, top face 330 below the top (spacer blocks), glued to all four",
         "walls. Tie strip on edge, centred, 155–195 below the top, glued to the front."),
        ("Seal corners.", "Acrylic bead in every inside corner you can reach now."),
        ("Back plate.", "Glue on with its biscuits and glue on the tie strip's end. Strap + cauls."),
        ("Last corners.", "Bead the back corners through the driver holes."),
        ("Finish.", "Sand 80 then 120, 2–3 coats of clear water-based lacquer, as Le Petit."),
        ("Cable + wool.", "Gland in, 4-core cable through, sealed. 300–500 g wool through the holes:",
         "lower half and corners, a hand's width free round each basket."),
        ("Drivers.", "+ to + on both. Battery test: both cones move out. Gasket, M5 × 16, crosswise."),
        ("Leak test.", "Push a cone in gently: it should come back slowly. A quick return = a leak."),
    )
    yy = y + 7
    for n, (title, *lines) in enumerate(steps, 1):
        s.text(x, yy, str(n), 1.9)
        s.text(x + 5, yy, title, 1.9)
        for ln in lines:
            s.text(x + 30, yy, ln, 1.9)
            yy += 3.6
        yy += 1.0

    yy += 5
    s.text(x, yy, "HARDWARE", 3.0)
    yy += 7
    for q, t in (("2", f"{sub.DRIVER_NAME}, 10\", 4 Ω"),
                 ("48", "biscuits, size 20"),
                 ("12", "M5 threaded inserts for wood (Ø6.5 drill)"),
                 ("12", "M5 × 16 pan head screws + washers"),
                 ("≈ 1.7 m", "gasket tape, 3 × 10 mm foam (2 × Ø250 rings)"),
                 ("1", f"{sub.GLAND_SIZE} cable gland + 4-core speaker cable, 2.5 mm²"),
                 ("300–500 g", "loose wool fill (sheep's wool or polyester)"),
                 ("", "PVA glue, clear lacquer, acrylic sealant")):
        s.text(x, yy, q, 1.9)
        s.text(x + 30, yy, t, 1.9)
        yy += 3.6

    frame(s, "Assembly and hardware", "n.t.s. @ A3", 3)
    return s


# single views cut out of the sheets for the web pages: (x, y, w, h) in sheet mm
DETAILS = {1: {"detail-c": (126, 171, 172, 76), "section-a-a": (14, 171, 120, 108),
               "section-b-b": (204, 25, 100, 142)}}


if __name__ == "__main__":
    sub.check()
    for n, fn in ((1, sheet1), (2, sheet2), (3, sheet3)):
        sh = fn()
        p = OUT / f"building-plan-sheet-{n}.svg"
        p.write_text(sh.svg())
        print("wrote", p.relative_to(OUT.parent.parent))
        for name, box in DETAILS.get(n, {}).items():
            p = OUT / f"{name}.svg"
            p.write_text(sh.svg(box))
            print("wrote", p.relative_to(OUT.parent.parent))
