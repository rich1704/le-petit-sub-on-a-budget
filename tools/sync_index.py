"""docs/index.md = README.md with the links rewritten for the website.

    python tools/sync_index.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/rich1704/le-petit-sub-on-a-budget"
SITE = "https://rich1704.github.io/le-petit-sub-on-a-budget/"

s = (ROOT / "README.md").read_text()
s = s.replace(f"📖 Also readable as a website, with the interactive 3D model: **{SITE}**",
              f"📂 All files, drawings and scripts: **{REPO}**")
s = s.replace(f"({SITE}3d-model/)", "(3d-model.md)")
s = s.replace("](docs/", "](")
s = s.replace("](tools/", f"]({REPO}/blob/main/tools/")
(ROOT / "docs" / "index.md").write_text(s)
print("wrote docs/index.md")
