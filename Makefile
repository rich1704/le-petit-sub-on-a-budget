# Regenerate every drawing, the diagram and the 3D stills from tools/sub.py.
PY ?= python3

all: check plans diagrams stills docs/index.md

check:
	$(PY) tools/sub.py

plans:
	$(PY) tools/make_building_plan.py
	$(PY) tools/make_cut_layout.py
	$(PY) tools/svg2png.py docs/plans/building-plan-sheet-1.svg docs/plans/building-plan-sheet-2.svg docs/plans/building-plan-sheet-3.svg

stills:
	$(PY) tools/shoot_3d.py

diagrams:
	$(PY) tools/make_diagrams.py

docs/index.md: README.md tools/sync_index.py
	$(PY) tools/sync_index.py

site: all
	mkdocs build --strict

.PHONY: all check plans diagrams stills site
