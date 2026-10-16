"""PNG previews of the A3 drawing sheets, rendered from the SVG with headless Chrome or Chromium.

    python tools/svg2png.py docs/plans/building-plan-sheet-*.svg
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium",
              "chromium-browser", "chrome")
PX = 2400                                  # PNG width; A3 landscape keeps 420:297


def chrome():
    for c in CANDIDATES:
        p = c if Path(c).exists() else shutil.which(c)
        if p:
            return p
    sys.exit("needs Chrome or Chromium for the PNG previews")


def render(svg: Path):
    h = round(PX * 297 / 420)
    html = (f'<!doctype html><html><body style="margin:0;background:#fff">'
            f'<img src="{svg.resolve().as_uri()}" style="width:{PX}px;height:{h}px;display:block"></body></html>')
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "sheet.html"
        page.write_text(html)
        out = svg.with_suffix(".png")
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        f"--window-size={PX},{h}", f"--screenshot={out.resolve()}", page.as_uri()],
                       check=True, capture_output=True)
        print("wrote", out)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        render(Path(a))
