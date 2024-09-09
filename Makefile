#
# Makefile for task-spread
#

# Define the place where to create the virtualenv
VENV ?= $(shell echo $${VIRTUAL_ENV:-$(HOME)/venv/ts})

# Package name
PKGNAME := async_flow_control

# ---------------------------------------------------------------------------

# Package version: taken from the __init__.py file
VERSION_FILE := src/$(PKGNAME)/__init__.py
VERSION	     := $(shell grep "^__version__" $(VERSION_FILE) | sed -r "s/__version__ = \"(.*)\"/\1/")

DATE		:= $(shell date -I)
BACKUP		:= $(PKGNAME)-$(VERSION)-$(DATE).tar.bz2
PKGFILE		:= dist/$(PKGNAME)-$(VERSION)-py3-none-any.whl
SRCD		:= $(PWD)
SETUP		:= $(SRCD)/setup.py

PYTHON_VERSION  ?= 3.12
VENV_PYTHON	:= $(VENV)/bin/python
PYTHON	:= $(shell if test -x $(VENV_PYTHON); then echo "$(VENV_PYTHON)"; else echo "python$(PYTHON_VERSION)"; fi)

# ---------------------------------------------------------------------------

all:
	@echo "VERSION: $(VERSION)"

pkg: venv $(PKGFILE)

clean:
	rm -rf $(BACKUP) $(PKGFILE) build src/${PKGNAME}.egg-info

backup: $(BACKUP)

# --------------------------------------------------------------------------

TEST ?= test/unit

venv: $(VENV)

pytest: $(VENV)/bin/pytest

unit: venv pytest
	PYTHONPATH=src:test $(VENV)/bin/pytest $(ARGS) $(TEST)

unit-verbose: venv pytest
	PYTHONPATH=src:test $(VENV)/bin/pytest -vv --capture=no $(ARGS) $(TEST)

install: local-install

reinstall: clean pkg local-clean local-install

reinstall[%]: clean pkg local-clean local-install[%]

# --------------------------------------------------------------------------

$(PKGFILE): $(VERSION_FILE) MANIFEST.in
	$(VENV_PYTHON) -m build -w

$(VENV):
	BASE=$$(basename "$@"); test -d "$$BASE" || mkdir -p "$$BASE"
	$(PYTHON) -m venv $@
	$@/bin/pip install --upgrade pip
	$@/bin/pip install wheel build

$(VENV)/bin/pytest:
	$(VENV)/bin/pip install pytest pytest-asyncio


# --------------------------------------------------------------------------
# Install locally the Python source package

local-install: $(VENV) $(PKGFILE)
	$(VENV)/bin/pip install --upgrade $(PKGFILE)$*

local-install[%]: $(VENV) $(PKGFILE)
	$(VENV)/bin/pip install --upgrade "$(PKGFILE)[$*]"

local-clean:
	$(VENV)/bin/pip uninstall -y $(PKGNAME)

# --------------------------------------------------------------------------

$(BACKUP):
	tar cvj -f $@ \
          --exclude=__pycache__ --exclude=\*~ \
	  --exclude=\*.\#\* --exclude=\*# --exclude=\*.old --exclude=old \
	  README.md Makefile doc/*.md src test

# -----------------------------------------------------------------------

$(VENV)/bin/twine:
	$(VENV)/bin/pip install twine

upload-check: $(PKGFILE) $(VENV)/bin/twine
	$(VENV)/bin/twine check $(PKGFILE)

upload-test: $(PKGFILE)
	$(VENV)/bin/twine upload --repository pypitest $(PKGFILE)

upload: $(PKGFILE)
	$(VENV)/bin/twine upload $(PKGFILE)
