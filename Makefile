PYTHON ?= python3
NVIM ?= nvim
GITSIGNS_RTP ?= ../gitsigns.nvim
SLOP_PLUGIN_ROOT ?= ../slop.nvim

.PHONY: demo render
demo:
	NVIM="$(NVIM)" GITSIGNS_RTP="$(GITSIGNS_RTP)" SLOP_PLUGIN_ROOT="$(SLOP_PLUGIN_ROOT)" $(PYTHON) demo/create.py

render:
	$(PYTHON) demo/render.py
