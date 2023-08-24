.PHONY: test install dev venv clean
.ONESHELL:

VENV=.venv
BASE=python3.11
PYTHON=./$(VENV)/bin/$(BASE)
PIP_INSTALL=$(PYTHON) -m pip install

test:
	$(PYTHON) -m unittest discover

install: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) .

dev: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) -e .[dev]
	pre-commit install

venv:
	test -d $(VENV) || $(BASE) -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete
