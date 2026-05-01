.PHONY: help install install-dev run test test-v check clean

UV ?= uv
VENV_PY := .venv/Scripts/python.exe
PYTHON ?= python

ifeq ($(wildcard $(VENV_PY)),$(VENV_PY))
PYTHON := $(VENV_PY)
endif

# Ensure local package imports work without installing editable.
export PYTHONPATH := src

help:
	@echo "Common development tasks:"
	@echo "  make install      Install package dependencies"
	@echo "  make install-dev  Install dev dependencies"
	@echo "  make run          Show CLI help"
	@echo "  make test         Run tests (quiet)"
	@echo "  make test-v       Run tests (verbose)"
	@echo "  make check        Run quick local checks"
	@echo "  make clean        Remove common cache files"

install:
	$(UV) sync

install-dev:
	$(UV) sync --dev

run:
	$(UV) run yt-xtract --help

test:
	$(PYTHON) -m pytest -q

test-v:
	$(PYTHON) -m pytest -vv

check: test

clean:
	$(PYTHON) -c "import pathlib, shutil; shutil.rmtree('.pytest_cache', ignore_errors=True); [shutil.rmtree(p, ignore_errors=True) for p in ('build', 'dist')]; [shutil.rmtree(path, ignore_errors=True) for path in pathlib.Path('.').rglob('__pycache__')]"
