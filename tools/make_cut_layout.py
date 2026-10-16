"""Cutting plan: the whole Le Petit Sub from one 2000 x 1000 mm board of 22 mm OSB.

    python tools/make_cut_layout.py      (from the repository root; needs matplotlib)

Writes docs/plans/cut-layout-2000x1000.{svg,png}. Two cuts straight across the board at 530 give
block A (both sides and the front) and block B (the back, then two 306 strips cut to 296 for top
and bottom; the braces come from the offcut beside the top). The rest of the board stays whole.
The script checks that nothing overlaps and that everything stays on the board, kerf included.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import sub  # noqa: E402

BW, BH = sub.SHEET
K, TR, T = sub.KERF, sub.TRIM, sub.T
OUT = Path(__file__).resolve().parent.parent / "docs" / "plans" / "cut-layout-2000x1000"


def layout():
    """(block, label, x, y, w, h): x along the 2000 mm length, y across the 1000 mm width."""
    parts = []
    xa, xb = TR, TR + sub.H + K
    y = TR
    for lab, size in (("Side 1", sub.ID), ("Side 2", sub.ID), ("Front", sub.W)):
        parts.append(("A", lab, xa, y, sub.H, size))
        y += size + K
    y = TR
    parts.append(("B", "Back", xb, y, sub.H, sub.W))
    y += sub.W + K
    for lab in ("Top", "Bottom"):
        parts.append(("B", lab, xb, y, sub.IW, sub.ID))
        if lab == "Top":    # braces: five 40 strips ripped from the offcut beside the top
            x = xb + sub.IW + K
            for blab, ln in (("Tie strip", sub.TIE["length"]), ("Window", sub.WIN["fb"]),
                             ("Window", sub.WIN["fb"]), ("Window", sub.WIN["side"]),
                             ("Window", sub.WIN["side"])):
                parts.append(("brace", blab, x, y, sub.STRIP, ln))
                x += sub.STRIP + K
        y += sub.ID + K
    cuts = [xa + sub.H, xb + sub.H]
    return parts, cuts


def check(parts, cuts):
    for _, lab, x, y, w, h in parts:
        assert x >= TR and y >= TR, lab
        assert x + w <= BW and y + h <= BH, f"{lab} runs off the board"
    for i, a in enumerate(parts):
        for b in parts[i + 1:]:
            ax, ay, aw, ah = a[2:]
            bx, by, bw, bh = b[2:]
            apart = (ax + aw + K <= bx or bx + bw + K <= ax or ay + ah + K <= by or by + bh + K <= ay)
            assert apart, f"{a[1]} and {b[1]} overlap"
    # every block part ends inside its block
    for blk, lab, x, y, w, h in parts:
        if blk in ("A", "B", "brace"):
            assert x + w <= cuts[1], lab
    spare = (BW - cuts[1] - K, BH - TR)
    return spare


def draw(parts, cuts, spare):
    ink, muted, offcut, wood, brace = "#16181a", "#5b5f63", "#ecebe7", "#f3e6cf", "#e9d3ac"
    fig, ax = plt.subplots(figsize=(16, 9.4))
    ax.add_patch(Rectangle((0, 0), BW, BH, fc=offcut, ec=ink, lw=1.4))
    ax.add_patch(Rectangle((0, 0), BW, TR, fc="#8a8f94", ec="none"))
    ax.add_patch(Rectangle((0, 0), TR, BH, fc="#8a8f94", ec="none"))
    for blk, lab, x, y, w, h in parts:
        ax.add_patch(Rectangle((x, y), w, h, fc=brace if blk == "brace" else wood, ec=ink, lw=1.0))
        if blk == "brace":
            ax.text(x + w / 2, y + h / 2, f"{lab} {h}", ha="center", va="center", rotation=90, fontsize=8,
                    color=ink)
        else:
            ax.text(x + w / 2, y + h / 2, f"{lab}\n{w} × {h}", ha="center", va="center", fontsize=10.5,
                    color=ink, linespacing=1.6)
    # offcut under the braces
    bx = max(p[2] + p[4] for p in parts if p[0] == "brace")
    by = min(p[3] for p in parts if p[0] == "brace")
    # spare
    sx = cuts[1] + K
    ax.add_patch(Rectangle((sx, TR), spare[0], spare[1], fc="#ffffff", ec=muted, lw=0.8, ls=(0, (4, 3))))
    ax.text(sx + spare[0] / 2, TR + spare[1] / 2 - 60, f"spare\n{spare[0]} × {spare[1]}\nstays whole", ha="center",
            va="center", fontsize=11, color=muted, linespacing=1.6)
    # the two cross cuts
    ax.plot([TR] * 2, [-30, BH + 30], color=ink, lw=1)
    for i, cx in enumerate(cuts):
        ax.plot([cx + K / 2] * 2, [-30, BH + 30], color=ink, lw=2.4)
        ax.text(cx + K / 2, BH + 42, f"cut {i + 3}", ha="center", va="bottom", fontsize=10, weight="bold",
                color=ink)
    for name, x0 in (("block A", TR), ("block B", TR + sub.H + K)):
        ax.text(x0 + sub.H / 2, BH + 42, name, ha="center", va="bottom", fontsize=10.5, weight="bold",
                color=ink)
        ax.text(x0 + sub.H / 2, -48, f"{sub.H}", ha="center", va="top", fontsize=9.5, color=muted)
    ax.text(sx + spare[0] / 2, -48, f"{spare[0]}", ha="center", va="top", fontsize=9.5, color=muted)
    # dashed line: the two 306 strips are stacked and cut to 296 together
    xb = TR + sub.H + K
    ax.plot([xb + sub.IW + K / 2] * 2, [TR + sub.W + K - 12, BH - TR + 2], color=ink, lw=1.1, ls=(0, (5, 3)))
    ax.annotate("braces: five 40 strips ripped along the 306,\nthen cut to 306 · 296 · 296 · 226 · 226",
                xy=(bx - 18, by + 150), xytext=(sx + 40, by + 330), fontsize=9, color=muted, va="center",
                arrowprops=dict(arrowstyle="-", color=muted, lw=0.8))
    ax.text(BW / 2, -100, "1 — trim one long edge, 10 mm: reference for every rip      "
            "2 — trim one end square to it, 10 mm: reference for both cross cuts      "
            "dashed — stack the two 306 strips, cut both to 296 at once", ha="center", va="top",
            fontsize=9, color=muted)
    ax.set_xlim(-30, BW + 30)
    ax.set_ylim(-150, BH + 165)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, BH + 128, "Cutting plan — the whole sub from one 2000 × 1000 mm board of 22 mm OSB",
            fontsize=13.5, weight="bold", color=ink)
    used = sum(w * h for *_, w, h in parts)
    ax.text(0, BH + 96, f"Every part drawn to scale · kerf {K} mm · {TR} mm trim on two edges · "
            f"two cross cuts · parts {used / 1e6:.2f} m² · spare {spare[0] * spare[1] / 1e6:.2f} m²",
            fontsize=9.5, color=muted)
    fig.tight_layout()
    for ext in ("svg", "png"):
        fig.savefig(OUT.with_suffix("." + ext), dpi=150, facecolor="#ffffff")
    plt.close(fig)
    return used


if __name__ == "__main__":
    sub.check()
    parts, cuts = layout()
    spare = check(parts, cuts)
    used = draw(parts, cuts, spare)
    print(f"{len(parts)} parts, no overlaps. Cross cuts at {cuts}. Parts {used / 1e6:.3f} m², "
          f"spare {spare[0]} x {spare[1]}.")
