# Regenerate every drawing, chart and the CamillaDSP config from tools/sub.py.
PY ?= python3
CAMILLADSP ?= camilladsp

all: check plans charts diagrams docs/index.md

check:
	$(PY) tools/sub.py

plans:
	$(PY) tools/make_building_plan.py
	$(PY) tools/make_cut_layout.py
	$(PY) tools/svg2png.py docs/plans/building-plan-sheet-1.svg docs/plans/building-plan-sheet-2.svg docs/plans/building-plan-sheet-3.svg

charts:
	$(PY) tools/make_charts.py

diagrams:
	$(PY) tools/make_diagrams.py

docs/index.md: README.md tools/sync_index.py
	$(PY) tools/sync_index.py

verify:
	$(PY) tools/verify_camilla.py $(CAMILLADSP)

site: all
	mkdocs build --strict

.PHONY: all check plans charts diagrams verify site
