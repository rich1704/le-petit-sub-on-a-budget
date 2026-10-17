"""Still images of the 3D model for the README (GitHub can't run the model itself).

    python tools/shoot_3d.py      (needs Chrome or Chromium; WebGL runs in software)

Serves docs/ on a local port and screenshots docs/3d/index.html in its screenshot mode (?shot).
"""
import functools
import http.server
import subprocess
import threading
from pathlib import Path

from svg2png import chrome

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "3d"
SHOTS = {"with-le-petit": "", "cut-open": "&view=front&pair=0", "exploded": "&view=explode&pair=0"}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(Quiet, directory=str(ROOT / "docs"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    try:
        for name, opts in SHOTS.items():
            out = OUT / f"{name}.png"
            subprocess.run([chrome(), "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                            "--hide-scrollbars", "--window-size=1600,900", "--virtual-time-budget=8000",
                            f"--screenshot={out}", f"http://127.0.0.1:{port}/3d/index.html?shot{opts}"],
                           check=True, capture_output=True)
            print("wrote", out.relative_to(ROOT))
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
