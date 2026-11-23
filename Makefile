PYTHON_SYS	?= python3
VENV		:= .venv
PYTHON		:= $(VENV)/bin/python
CONFIG		?= config.txt

MYPY_FLAGS	:= --warn-return-any --warn-unused-ignores \
		   --ignore-missing-imports --disallow-untyped-defs \
		   --check-untyped-defs

.PHONY: all install run debug test lint lint-strict package clean fclean re

all: install

$(PYTHON):
	$(PYTHON_SYS) -m venv $(VENV)

install: $(PYTHON)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(PYTHON_SYS) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON_SYS) -m pdb a_maze_ing.py $(CONFIG)

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

package:
	$(PYTHON) -m build --outdir .
	rm -rf build *.egg-info

clean:
	find . -path ./$(VENV) -prune -o -type d -name "__pycache__" \
		-exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist *.egg-info

fclean: clean
	rm -rf $(VENV)

re: fclean install
