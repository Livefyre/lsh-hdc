.PHONY: clean virtualenv upgrade test package dev

PYENV = . env/bin/activate;
PYTHON = $(PYENV) python
CUSTOM_PKG_REPO=http://packages.livefyre.com/buildout/packages/

package: env
	$(PYTHON) setup.py bdist_egg
	$(PYTHON) setup.py sdist

test: env dev
	$(PYENV) nosetests --with-doctest $(NOSEARGS)

dev: env/bin/activate dev_requirements.txt
	$(PYENV) pip install --process-dependency-links -e . -r dev_requirements.txt --find-links $(CUSTOM_PKG_REPO)

clean:
	$(PYTHON) setup.py clean
	find . -type f -name "*.pyc" -exec rm {} \;

nuke: clean
	rm -rf *.egg *.egg-info env bin cover coverage.xml nosetests.xml

env virtualenv: env/bin/activate
env/bin/activate: requirements.txt setup.py
	test -f env/bin/activate || virtualenv --no-site-packages env
	ln -fs env/bin .
	$(PYENV) pip install --process-dependency-links -e . -r requirements.txt --find-links $(CUSTOM_PKG_REPO)
	touch env/bin/activate

upgrade:
	test -f env/bin/activate || virtualenv --no-site-packages env
	ln -fs env/bin .
	$(PYENV) pip install --process-dependency-links -e . -r requirements.txt --upgrade --find-links $(CUSTOM_PKG_REPO)
	touch env/bin/activate
