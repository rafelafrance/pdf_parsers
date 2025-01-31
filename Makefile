.PHONY: test install dev venv clean
.ONESHELL:

test:
	. .venv/bin/activate
	python3.11 -m unittest discover

install: venv
	. .venv/bin/activate
	python3.11 -m pip install -U pip setuptools wheel
	python3.11 -m pip install git+https://github.com/rafelafrance/common_utils.git@main#egg=common_utils
	python3.11 -m pip install git+https://github.com/rafelafrance/traiter.git@master#egg=traiter
	python3.11 -m pip install .
	python3.11 -m spacy download en_core_web_sm

dev: venv
	. .venv/bin/activate
	python3.11 -m pip install -U pip setuptools wheel
	python3.11 -m pip install -e ../../misc/common_utils
	python3.11 -m pip install -e ../../traiter/traiter
	python3.11 -m pip install -e .[dev]
	python3.11 -m spacy download en_core_web_sm
	pre-commit install

venv:
	test -d .venv || python3.11 -m venv .venv

clean:
	rm -r .venv
	find -iname "*.pyc" -delete
