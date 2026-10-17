"""Predictions for the Le Petit Sub from the driver's datasheet, the charts that show them, and the
CamillaDSP example that implements the DSP.

    python tools/make_charts.py      (needs numpy + matplotlib)

Model: the SB26SFCL38-4's own Thiele/Small parameters (Re, Bl, Mms, Cms, Rms, Sd) in a sealed box,
both drivers in the same box (each works into half of it), radiating into half space at 1 m: the sub
on the floor, without room gain. The DSP filters are the analogue prototypes of CamillaDSP's biquads,
which match the digital filters closely below 300 Hz at 48 kHz.

Writes docs/assets/charts/*.png, docs/dsp/le-petit-sub.yml and prints every number the docs quote.
"""
import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

import sub  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "docs" / "assets" / "charts"
D = sub.DRIVER

# DSP settings - the docs, the YAML and the charts all read these
XO = 80.0                       # crossover, LR4 (24 dB/oct) on both sides
LT_TARGET = (25.0, 0.707)       # Linkwitz transform target: f, Q
SUBSONIC = (18.0, 2)            # Butterworth high-pass: f, order
V_LIMIT = 18.0                  # V per channel at the amp output: 18² / 4 Ω ≈ 80 W, the driver's rating
V_REF = 2.83

INK, MUTED, GRID, BG = "#16181a", "#5b5f63", "#e4e4df", "#fbfbf9"
BLUE, ORANGE, GREEN, PURPLE = "#2a78d6", "#e8653a", "#12a679", "#7a5bd0"
F = np.geomspace(10, 300, 600)


# ------------------------------------------------------------------ model
def box_compliance():
    vb = sub.volumes()["net"] / sub.N_DRV / 1000
    cab = vb / (sub.RHO * sub.C0 ** 2 * D["Sd"] ** 2)
    return D["Cms"] * cab / (D["Cms"] + cab)


def velocity(f, V):
    s = 2j * np.pi * np.asarray(f)
    Ze = D["Re"] + 0 * s        # Le left out: a lumped 1 mH tilts the band, the datasheet curve is flat to 1 kHz
    Zm = D["Rms"] + s * D["Mms"] + 1 / (s * box_compliance())
    return D["Bl"] * V / (Ze * Zm + D["Bl"] ** 2)


def excursion(f, V):
    return np.abs(velocity(f, V) / (2j * np.pi * np.asarray(f)))


def spl(f, V, H=1.0):
    """Both drivers, half space, 1 m; V per channel; H = complex DSP response in front."""
    s = 2j * np.pi * np.asarray(f)
    U = sub.N_DRV * D["Sd"] * velocity(f, V) * H
    return 20 * np.log10(np.abs(s * sub.RHO * U / (2 * np.pi)) / 2e-5)


def fc_qtc():
    """Box resonance and Q from the electro-mechanical model (includes Qms)."""
    fc = 1 / (2 * math.pi * math.sqrt(D["Mms"] * box_compliance()))
    wc = 2 * math.pi * fc
    qm = wc * D["Mms"] / D["Rms"]
    qe = wc * D["Mms"] * D["Re"] / D["Bl"] ** 2
    return fc, qm * qe / (qm + qe)


# ------------------------------------------------------------------ filters (analogue prototypes)
def so(f, f0, q, kind):
    s = 1j * np.asarray(f) / f0
    den = s ** 2 + s / q + 1
    return {"lp": 1 / den, "hp": s ** 2 / den}[kind]


def linkwitz(f, fa, qa, ft, qt):
    sa, st = 1j * np.asarray(f) / fa, 1j * np.asarray(f) / ft
    return (sa ** 2 + sa / qa + 1) / (st ** 2 + st / qt + 1) * (fa / ft) ** 2


def lr4(f, f0, kind):
    return so(f, f0, 1 / math.sqrt(2), kind) ** 2


def butter_hp(f, f0, order):
    assert order == 2
    return so(f, f0, 1 / math.sqrt(2), "hp")


def chain(f):
    fc, qtc = fc_qtc()
    lt = linkwitz(f, fc, qtc, *LT_TARGET)
    lp = lr4(f, XO, "lp")
    hp = butter_hp(f, *SUBSONIC)
    return lt, lp, hp, lt * lp * hp


def db(x):
    return 20 * np.log10(np.abs(x))


def corner(f, y, ref, drop=-3.0):
    """Lowest frequency where y is within `drop` of ref, interpolated."""
    i = np.argmax(y - ref >= drop)
    return float(np.interp(ref + drop, [y[i - 1], y[i]], [f[i - 1], f[i]]))


# ------------------------------------------------------------------ charts
def style(ax, ylabel, xlim=(10, 300)):
    ax.set_xscale("log")
    ax.set_xlim(*xlim)
    ticks = [t for t in (10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400) if xlim[0] <= t <= xlim[1]]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlabel("frequency (Hz)", color=MUTED)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_facecolor(BG)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color("#bdbdb6")
    ax.tick_params(colors=MUTED, length=0)


def fig():
    plt.rcParams.update({"font.family": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 11})
    f_, ax = plt.subplots(figsize=(8, 4.4))
    f_.patch.set_facecolor(BG)
    return f_, ax


def save(f_, name):
    f_.tight_layout()
    f_.savefig(CH / f"{name}.png", dpi=200, facecolor=BG)
    plt.close(f_)
    print("wrote", (CH / f"{name}.png").relative_to(ROOT))


def legend(ax, loc=None, ncol=2):
    """Above the plot, so it never covers a curve."""
    lg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=ncol, frameon=False, fontsize=10,
                   handlelength=1.6, columnspacing=1.6, borderaxespad=0)
    for t in lg.get_texts():
        t.set_color(INK)


def chart_response(n):
    lt, lp, hp, tot = chain(F)
    box = spl(F, V_REF)
    f_, ax = fig()
    ax.plot(F, box, color=ORANGE, lw=2, label=f"sealed box alone (Fc {n['fc']:.0f} Hz, Q {n['qtc']:.2f})")
    ax.plot(F, spl(F, V_REF, lt), color=GREEN, lw=2, label=f"+ Linkwitz transform → {LT_TARGET[0]:.0f} Hz, Q 0.71")
    ax.plot(F, spl(F, V_REF, tot), color=BLUE, lw=2.4,
            label=f"the sub: + {XO:.0f} Hz LR4 low-pass + {SUBSONIC[0]:.0f} Hz subsonic")
    ref = n["ref_db"]
    ax.axhline(ref - 3, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.text(10.6, ref - 2.4, "−3 dB", color=MUTED, fontsize=9.5)
    for x, c in ((n["f3_box"], ORANGE), (n["f3_lt"], GREEN)):
        ax.plot([x], [ref - 3], "o", ms=6, color=c, mec=BG, mew=1.5)
        ax.annotate(f"{x:.0f} Hz", (x, ref - 3), xytext=(0, -16), textcoords="offset points", ha="center",
                    fontsize=9.5, color=INK)
    style(ax, f"SPL at {V_REF} V, 1 m (dB)")
    ax.set_ylim(ref - 33, ref + 7)
    legend(ax)
    save(f_, "response")


def chart_dsp():
    lt, lp, hp, tot = chain(F)
    f_, ax = fig()
    ax.plot(F, db(lt), color=GREEN, lw=2, label="Linkwitz transform")
    ax.plot(F, db(lp), color=ORANGE, lw=2, label=f"low-pass, LR4 {XO:.0f} Hz")
    ax.plot(F, db(hp), color=PURPLE, lw=2, label=f"subsonic, Butterworth {SUBSONIC[0]:.0f} Hz")
    ax.plot(F, db(tot), color=BLUE, lw=2.4, label="all three together")
    i = np.argmax(db(tot))
    ax.plot([F[i]], [db(tot)[i]], "o", ms=6, color=BLUE, mec=BG, mew=1.5)
    ax.annotate(f"+{db(tot)[i]:.1f} dB at {F[i]:.0f} Hz", (F[i], db(tot)[i]), xytext=(-6, -24),
                textcoords="offset points", fontsize=9.5, color=INK)
    ax.axhline(0, color=MUTED, lw=0.8)
    style(ax, "gain (dB)")
    ax.set_ylim(-30, 22)
    legend(ax)
    save(f_, "dsp-filters")


def chart_excursion():
    f_, ax = fig()
    x = excursion(F, V_LIMIT) * 1000
    ax.axhspan(D["xmax"] * 1000, 12, color="#f3e3dc", lw=0)
    ax.axhline(D["xmax"] * 1000, color=ORANGE, lw=1.2, ls=(0, (5, 3)))
    ax.text(10.6, D["xmax"] * 1000 + 0.35, f"Xmax {D['xmax'] * 1000:.1f} mm (datasheet: 15.8 mm p-p linear travel)",
            color=INK, fontsize=9.5)
    ax.plot(F, x, color=BLUE, lw=2.4, label=f"cone excursion at the limiter, {V_LIMIT:.0f} V per channel")
    i = np.argmax(x)
    ax.plot([F[i]], [x[i]], "o", ms=6, color=BLUE, mec=BG, mew=1.5)
    ax.annotate(f"{x[i]:.1f} mm peak, {100 * x[i] / (D['xmax'] * 1000):.0f} % of Xmax", (F[i], x[i]),
                xytext=(10, 10), textcoords="offset points", fontsize=9.5, color=INK)
    style(ax, "peak excursion (mm)")
    ax.set_ylim(0, 10)
    legend(ax)
    save(f_, "excursion")


def chart_max_spl():
    f_, ax = fig()
    v_x = D["xmax"] / excursion(F, 1.0)
    vlim = spl(F, V_LIMIT)
    xlim = spl(F, v_x)
    ax.plot(F, xlim, color=ORANGE, lw=2, ls=(0, (5, 3)), label=f"cone at Xmax ({v_x.min():.0f}–{v_x[F < 70].max():.0f} V, "
            f"more than the {D['P']:.0f} W rating)")
    ax.plot(F, vlim, color=BLUE, lw=2.4, label=f"at the limiter, {V_LIMIT:.0f} V ≈ {V_LIMIT ** 2 / D['Z']:.0f} W per driver")
    for fx in (20, 30, 40, 60):
        y = float(np.interp(fx, F, vlim))
        ax.plot([fx], [y], "o", ms=6, color=BLUE, mec=BG, mew=1.5)
        ax.annotate(f"{y:.0f}", (fx, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9.5,
                    color=INK)
    style(ax, "max SPL, 1 m, on the floor (dB)", (15, 200))
    ax.set_ylim(80, 125)
    legend(ax)
    save(f_, "max-spl")


def chart_crossover():
    f_, ax = fig()
    lp, hp = lr4(F, XO, "lp"), lr4(F, XO, "hp")
    ax.plot(F, db(lp), color=BLUE, lw=2.2, label=f"sub: LR4 low-pass {XO:.0f} Hz")
    ax.plot(F, db(hp), color=ORANGE, lw=2.2, label=f"Le Petit: LR4 high-pass {XO:.0f} Hz")
    ax.plot(F, db(lp + hp), color=INK, lw=1.6, ls=(0, (5, 3)), label="sum, in phase: flat")
    ax.axhline(-6, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax.text(21, -5.2, "−6 dB at the crossover", color=MUTED, fontsize=9.5)
    style(ax, "level (dB)", (20, 300))
    ax.set_ylim(-36, 6)
    legend(ax)
    save(f_, "crossover")


# ------------------------------------------------------------------ CamillaDSP
def camilla_yaml(n):
    fc, qtc = n["fc"], n["qtc"]
    head = -math.ceil(n["dsp_peak"])
    return f"""# Le Petit + Le Petit Sub - CamillaDSP v4, example pipeline
# Generated by tools/make_charts.py from the driver datasheet and the box. A STARTING POINT:
# set sub_level, sub_delay and limiter_db by measurement (docs/02-amp-and-dsp.md).
#
# Outputs: 0 = Le Petit L, 1 = Le Petit R, 2 = sub (mono, Y-cable to both TPA3255 inputs),
#          3 = sub copy (optional: the second TPA3255 input from its own output instead of a Y-cable)
# Keep your own `devices:` section - only the playback device needs 4 channels.

devices:
  samplerate: 48000
  chunksize: 1024
  capture:
    type: Stdin            # replace with your capture device
    channels: 2
    format: S32_LE
  playback:
    type: Stdout           # replace with your 4-channel output (e.g. UMC404HD)
    channels: 4
    format: S32_LE

mixers:
  to_sub:
    channels: {{in: 2, out: 4}}
    mapping:
      - dest: 0
        sources: [{{channel: 0, gain: 0, scale: dB}}]
      - dest: 1
        sources: [{{channel: 1, gain: 0, scale: dB}}]
      - dest: 2              # mono sum, -6 dB each: a centred sound keeps its level
        sources: [{{channel: 0, gain: -6.02, scale: dB}}, {{channel: 1, gain: -6.02, scale: dB}}]
      - dest: 3
        sources: [{{channel: 0, gain: -6.02, scale: dB}}, {{channel: 1, gain: -6.02, scale: dB}}]

filters:
  lepetit_hp:              # Le Petit: high-pass at the crossover (replaces its protective high-pass)
    type: BiquadCombo
    parameters: {{type: LinkwitzRileyHighpass, freq: {XO:.0f}, order: 4}}
  sub_headroom:            # the filters below boost up to +{n['dsp_peak']:.1f} dB: make room first
    type: Gain
    parameters: {{gain: {head}, scale: dB}}
  sub_lt:                  # sealed box Fc {fc:.1f} Hz / Qtc {qtc:.2f} -> {LT_TARGET[0]:.0f} Hz / Q {LT_TARGET[1]}
    type: Biquad
    parameters: {{type: LinkwitzTransform, freq_act: {fc:.1f}, q_act: {qtc:.2f}, freq_target: {LT_TARGET[0]:.0f}, q_target: {LT_TARGET[1]}}}
  sub_lp:
    type: BiquadCombo
    parameters: {{type: LinkwitzRileyLowpass, freq: {XO:.0f}, order: 4}}
  sub_subsonic:            # required: keeps the transform's boost off the infrasonic
    type: BiquadCombo
    parameters: {{type: ButterworthHighpass, freq: {SUBSONIC[0]:.0f}, order: {SUBSONIC[1]}}}
  sub_level:               # set by measurement: sub and Le Petit at the same level round {XO:.0f} Hz
    type: Gain
    parameters: {{gain: 0.0, scale: dB}}
  sub_delay:               # set by measurement: the sum at {XO:.0f} Hz at its loudest
    type: Delay
    parameters: {{delay: 0.0, unit: ms, subsample: false}}
  sub_limiter:             # {V_LIMIT:.0f} V at the amp output: clip_limit = 20 log10({V_LIMIT:.0f} / volts at 0 dBFS)
    type: Limiter
    parameters: {{clip_limit: -6.0, soft_clip: false}}

pipeline:
  - type: Mixer
    name: to_sub
  - type: Filter
    channels: [0, 1]
    names: [lepetit_hp]
  - type: Filter
    channels: [2, 3]
    names: [sub_headroom, sub_lt, sub_lp, sub_subsonic, sub_level, sub_delay, sub_limiter]
"""


def numbers():
    fc, qtc = fc_qtc()
    v = sub.volumes()
    a = sub.alignment()
    lt, lp, hp, tot = chain(F)
    ref = float(spl(np.array([2000.0]), V_REF)[0])     # the passband level, above the box's hump
    box, ltr = spl(F, V_REF), spl(F, V_REF, lt)
    n = dict(fc=fc, qtc=qtc, fc_simple=a["fc"], qtc_simple=a["qtc"], ref_db=ref,
             f3_box=corner(F, box, ref), f3_lt=corner(F, ltr, ref), dsp_peak=float(db(tot).max()),
             lt_boost_dc=40 * math.log10(fc / LT_TARGET[0]))
    n["x_limit_max"] = float(excursion(F, V_LIMIT).max() * 1000)
    n["v_xmax_min"] = float((D["xmax"] / excursion(F, 1.0)).min())
    n.update(v)
    return n


def spl_limit():
    return {fx: float(spl(np.array([fx]), V_LIMIT)[0]) for fx in (20, 25, 30, 40, 60, 80)}


if __name__ == "__main__":
    sub.check()
    CH.mkdir(parents=True, exist_ok=True)
    n = numbers()
    chart_response(n)
    chart_dsp()
    chart_excursion()
    chart_max_spl()
    chart_crossover()
    y = ROOT / "docs" / "dsp" / "le-petit-sub.yml"
    y.parent.mkdir(exist_ok=True)
    y.write_text(camilla_yaml(n))
    print("wrote", y.relative_to(ROOT))
    print(f"net {n['net']:.1f} l; Fc {n['fc']:.1f} Hz Qtc {n['qtc']:.2f} (closed form {n['fc_simple']:.1f} / "
          f"{n['qtc_simple']:.2f}); passband {n['ref_db']:.1f} dB @ {V_REF} V; -3 dB box {n['f3_box']:.0f} Hz, "
          f"with LT {n['f3_lt']:.0f} Hz; DSP peak +{n['dsp_peak']:.1f} dB, LT boost at DC +{n['lt_boost_dc']:.1f} dB")
    print("max SPL at the limiter: " + ", ".join(f"{k} Hz {v:.1f} dB" for k, v in spl_limit().items()))
    print(f"excursion at the limiter max {n['x_limit_max']:.1f} mm; Xmax reached at >= {n['v_xmax_min']:.1f} V")
