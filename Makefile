PYTHON_VENV=.venv/bin/python
PYTHON=$(shell if test -f ${PYTHON_VENV}; then echo ${PYTHON_VENV}; else echo ${SYSTEM_PYTHON}; fi)

install:
	$(PYTHON) -m pip install -e .

install_dev:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest -x -s -vv
