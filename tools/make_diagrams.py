"""The two web diagrams: how the opposed drivers work, and the signal chain.

    python tools/make_diagrams.py   ->  docs/assets/diagrams/{opposed-drivers,signal-chain}.svg
"""
from pathlib import Path

import sub

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "diagrams"
INK, MUTED, WOOD, WOOD_E, ACCENT, DRV, MAG = "#16181a", "#5b5f63", "#e9d9bd", "#8a6d3b", "#c4512a", "#8a9097", "#4a4f55"
FONT = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'
STYLE = ('<style>text{paint-order:stroke;stroke:#ffffff;stroke-width:4px;stroke-linejoin:round}'
         '.m{font-family:Menlo,Consolas,monospace;font-size:12px}</style>')


def opposed():
    """Top section at driver height, to scale (1 mm = 1.1 px), front at the bottom."""
    k, ox, oy = 1.1, 270, 92
    W, D, T = sub.W, sub.D, sub.T

    def X(u):
        return ox + u * k

    def Y(w):
        return oy + w * k

    def rect(u, w, du, dw, fill=WOOD, stroke=INK, sw=1.4, extra=""):
        return (f'<rect x="{X(u):.1f}" y="{Y(w):.1f}" width="{du * k:.1f}" height="{dw * k:.1f}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def poly(pts, fill, stroke=INK, sw=1.2):
        p = " ".join(f"{X(u):.1f},{Y(w):.1f}" for u, w in pts)
        return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

    e = []
    e.append(rect(T, T, sub.IW, sub.ID, fill="#faf8f3", stroke="none"))
    wc = T + sub.DRV_U
    rr, rc = sub.RECESS / 2, sub.CUTOUT / 2
    for side in (-1, 1):
        u0 = 0 if side < 0 else W - T

        def U(d):
            return d if side < 0 else W - d
        for a, b, inner in ((T, wc - rr, False), (wc - rr, wc - rc, True), (wc + rc, wc + rr, True),
                            (wc + rr, D - T, False)):
            th = T - (sub.RECESS_DEPTH if inner else 0)
            uu = u0 + (sub.RECESS_DEPTH if inner and side < 0 else 0)
            e.append(rect(uu, a, th, b - a))
        back = sub.RECESS_DEPTH + sub.DRIVER["depth"]
        mg = back - 34
        rb, rm = sub.DRIVER["basket"] / 2, sub.DRIVER["magnet"] / 2
        for sg in (-1, 1):
            e.append(poly([(U(3.5), wc + sg * rb), (U(3.5), wc + sg * (rb - 6)), (U(mg), wc + sg * 30),
                           (U(mg), wc + sg * 36)], DRV))
        e.append(poly([(U(0), wc - 132.5), (U(3.5), wc - 132.5), (U(3.5), wc + 132.5), (U(0), wc + 132.5)], DRV))
        e.append(poly([(U(mg), wc - rm), (U(back), wc - rm), (U(back), wc + rm), (U(mg), wc + rm)], MAG))
        e.append(poly([(U(0), wc - 103), (U(0), wc + 103), (U(55), wc + 20), (U(55), wc - 20)], "#ffffff"))
        # the cone moves out: arrow outside, and the reaction on the box points inwards
        xa = X(U(-14))
        x2 = X(U(-70))
        e.append(f'<path d="M{xa:.1f} {Y(wc):.1f} H{x2 + 10 * (1 if side < 0 else -1):.1f}" stroke="{ACCENT}" stroke-width="3" fill="none"/>')
        o = -1 if side < 0 else 1          # outwards
        e.append(f'<polygon points="{x2:.1f},{Y(wc):.1f} {x2 - 13 * o:.1f},{Y(wc) - 7:.1f} '
                 f'{x2 - 13 * o:.1f},{Y(wc) + 7:.1f}" fill="{ACCENT}"/>')
        lx = X(U(-48))
        e.append(f'<text x="{lx:.1f}" y="{Y(wc) - 16:.1f}" font-size="13" fill="{ACCENT}" text-anchor="middle">'
                 f'cone out</text>')
        fx = X(U(T + 30))
        e.append(f'<text x="{fx + (14 if side < 0 else -14):.1f}" y="{Y(wc + 150):.1f}" font-size="12" fill="{MUTED}" '
                 f'text-anchor="{"start" if side < 0 else "end"}">box pushed {"right" if side < 0 else "left"}</text>')
    e.append(rect(0, 0, W, T))
    e.append(rect(0, D - T, W, T))
    tu = W / 2 - T / 2
    e.append(rect(tu, T, T, sub.ID, fill="#d8c3a0"))
    gap = (W / 2 - T / 2) - (sub.RECESS_DEPTH + sub.DRIVER["depth"])
    e.append(f'<text x="{X(W / 2):.1f}" y="{Y(-14):.1f}" font-size="12.5" fill="{MUTED}" text-anchor="middle">'
             f'back</text>')
    e.append(f'<text x="{X(W / 2):.1f}" y="{Y(D + 24):.1f}" font-size="12.5" fill="{MUTED}" text-anchor="middle">'
             f'front — {W} mm, like Le Petit</text>')
    e.append(f'<text x="{X(W / 2) + 18:.1f}" y="{Y(48):.1f}" font-size="12" fill="{INK}">tie strip</text>')
    e.append(f'<text x="{X(W / 2):.1f}" y="{Y(wc + 112):.1f}" font-size="12" fill="{INK}" text-anchor="middle">'
             f'{gap:.0f} mm clear to each magnet</text>')
    h = Y(D + 60)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {h:.0f}" {FONT} role="img" '
            f'aria-label="Top section of the sub at driver height: two drivers in the side panels, magnets facing '
            f'each other, both cones move outwards together so the forces on the box cancel.">{STYLE}'
            f'<rect width="900" height="{h:.0f}" fill="#ffffff"/>'
            f'<text x="30" y="34" font-size="18" font-weight="700" fill="{INK}">Two drivers, opposed: '
            f'the pushes on the box cancel</text>'
            f'<text x="30" y="56" font-size="12.5" fill="{MUTED}">Top section at driver height, to scale. '
            f'Same signal, mirrored mounting: both cones move out together, then in together.</text>'
            + "".join(e) + "</svg>\n")


def signal_chain():
    def box(x, y, w, h, title, sub_=None, bold=False, top=False):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>'
        ty = y + 24 if top else y + h / 2 + (-4 if sub_ else 5)
        s += (f'<text x="{x + w / 2}" y="{ty}" font-size="14" text-anchor="middle" fill="{INK}"'
              f'{" font-weight=" + chr(34) + "600" + chr(34) if bold else ""}>{title}</text>')
        if sub_:
            s += f'<text x="{x + w / 2}" y="{ty + 17}" font-size="11.5" text-anchor="middle" fill="{MUTED}">{sub_}</text>'
        return s

    def wire(d, c=INK, w=1.6, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"{da}/>'

    def lab(x, y, t, cls="m", anchor="end", c=INK):
        return f'<text x="{x}" y="{y}" class="{cls}" font-size="13" text-anchor="{anchor}" fill="{c}">{t}</text>'

    e = [box(20, 120, 130, 60, "Music", "stereo source"),
         box(200, 110, 170, 80, "CamillaDSP", "crossover · LT · limiter", True),
         box(420, 60, 150, 180, "4-out interface", None, True, True),
         box(650, 30, 120, 56, "Le Petit amp", "e.g. A70"),
         box(650, 190, 120, 70, "TPA3255", "stereo board, 48 V"),
         box(820, 20, 100, 38, "Le Petit L"), box(820, 64, 100, 38, "Le Petit R"),
         box(820, 176, 100, 42, "sub, left driver"), box(820, 232, 100, 42, "sub, right driver")]
    e += [wire("M150 150 H200"), wire("M370 150 H420")]
    e += [lab(562, 112, "OUT 1"), lab(562, 136, "OUT 2"), lab(562, 186, "OUT 3"), lab(562, 210, "OUT 4 · spare", c=MUTED)]
    e += [wire("M570 108 H610 V50 H650"), wire("M570 132 H620 V66 H650")]
    e += [wire("M770 50 H795 V39 H820"), wire("M770 66 H795 V83 H820")]
    e += [wire("M570 182 H630 V212 H650", c=ACCENT, w=2.2), wire("M630 182 V238 H650", c=ACCENT, w=2.2)]
    e += [lab(640, 176, "Y", cls="s", anchor="middle", c=ACCENT)]
    e += [wire("M770 212 H795 V197 H820", c=ACCENT, w=2.2), wire("M770 238 H795 V253 H820", c=ACCENT, w=2.2)]
    e += [f'<text x="20" y="300" font-size="12" fill="{MUTED}">Le Petit: LR4 high-pass 80 Hz. '
          f'Sub: mono sum → Linkwitz transform → LR4 low-pass 80 Hz → 18 Hz subsonic → level, delay → '
          f'limiter 18 V.</text>',
          f'<text x="20" y="318" font-size="12" fill="{MUTED}">One mono sub output, split to both board inputs '
          f'(or OUT 3 + OUT 4 with the same signal). Both drivers wired + to +.</text>']
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 332" {FONT} role="img" '
            f'aria-label="Signal chain: music into CamillaDSP, out of a 4-output interface. Outputs 1 and 2 drive '
            f'Le Petit through its amp; output 3 feeds both inputs of the TPA3255 board, one channel per sub driver.">'
            f'{STYLE}<rect width="940" height="332" fill="#ffffff"/>' + "".join(e) + "</svg>\n")


if __name__ == "__main__":
    sub.check()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("opposed-drivers", opposed), ("signal-chain", signal_chain)):
        (OUT / f"{name}.svg").write_text(fn())
        print("wrote", f"docs/assets/diagrams/{name}.svg")
