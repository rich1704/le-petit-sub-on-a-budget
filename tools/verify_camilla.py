"""Check docs/dsp/le-petit-sub.yml with the real CamillaDSP binary: render an impulse through it
(file backends, no audio hardware) and compare both outputs with the filters the charts are drawn from.

    python tools/verify_camilla.py [path/to/camilladsp]      (needs numpy + pyyaml)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml

import make_charts as m

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "docs" / "dsp" / "le-petit-sub.yml"
TOL = 0.25                     # dB, 15-200 Hz (sub) and 40-300 Hz (Le Petit)


def render(cfg, x, camilladsp):
    fs = int(cfg["devices"]["samplerate"])
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        x.astype(np.float32).tofile(d / "in.raw")
        cfg = dict(cfg, devices={"samplerate": fs, "chunksize": 1024,
                                 "capture": {"type": "RawFile", "channels": x.shape[1], "filename": str(d / "in.raw"),
                                             "format": "F32_LE", "extra_samples": fs},
                                 "playback": {"type": "File", "channels": 4, "filename": str(d / "out.raw"),
                                              "format": "F32_LE"}})
        (d / "cfg.yml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        r = subprocess.run([camilladsp, str(d / "cfg.yml")], capture_output=True, text=True, timeout=120)
        if r.returncode or not (d / "out.raw").exists():
            sys.exit(f"camilladsp failed:\n{r.stderr[-1500:]}")
        return np.fromfile(d / "out.raw", np.float32).reshape(-1, 4)


if __name__ == "__main__":
    exe = sys.argv[1] if len(sys.argv) > 1 else "camilladsp"
    cfg = yaml.safe_load(CFG.read_text())
    fs, n, amp = 48000, 1 << 17, 0.01
    x = np.zeros((n, 2))
    x[1024, :] = amp                            # both inputs: the mono sum (-6.02 dB each) is unity
    y = render(cfg, x, exe)[:n]
    f = np.fft.rfftfreq(n, 1 / fs)
    head = cfg["filters"]["sub_headroom"]["parameters"]["gain"]
    lt, lp, hp, tot = m.chain(f)
    worst = 0.0
    for ch, ref, lo, hi, name in ((2, tot * 10 ** (head / 20), 15, 200, "sub"),
                                  (0, m.lr4(f, m.XO, "hp"), 40, 300, "Le Petit")):
        H = np.fft.rfft(y[:, ch]) / (amp * np.exp(-2j * np.pi * f * 1024 / fs))
        sel = (f >= lo) & (f <= hi)
        dev = np.abs(m.db(H[sel]) - m.db(ref[sel]))
        worst = max(worst, float(dev.max()))
        print(f"{name:9s} {lo}-{hi} Hz: CamillaDSP vs model, max {dev.max():.3f} dB")
    print("OK" if worst <= TOL else f"FAIL: more than {TOL} dB")
    sys.exit(0 if worst <= TOL else 1)
