PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: install test benchmark clean

install:
	$(PIP) install -e ".[dev]"

test:
	PYTHONPATH=python $(PYTHON) -m pytest tests/ -v

benchmark:
	$(PYTHON) scripts/run_phase06_partial.py --repo-root .

clean:
	rm -rf dist/ build/ *.egg-info
