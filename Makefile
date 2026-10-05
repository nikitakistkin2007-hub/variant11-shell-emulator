PYTHON ?= python3

.PHONY: test run demo

test:
	$(PYTHON) -m unittest discover -s tests -v

run:
	$(PYTHON) src/main.py --vfs vfs_demo

demo:
	PYTHON=$(PYTHON) bash scripts/demo.sh
