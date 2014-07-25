.PHONY: clean virtualenv upgrade test package dev

PYENV = . env/bin/activate;
PYTHON = $(PYENV) python

package: env
	$(PYTHON) setup.py bdist_egg
	$(PYTHON) setup.py sdist
<<<<<<< HEAD

dev: env/bin/activate dev_requirements.txt
	$(PYENV) pip install -e . -r dev_requirements.txt

test: env
	$(PYENV) nosetests $(NOSEARGS)
=======

test: env dev
	$(PYENV) nosetests $(NOSEARGS)

dev: env/bin/activate dev_requirements.txt
	$(PYENV) pip install -e . -r dev_requirements.txt
>>>>>>> 6d6e0de21b2eee7c2c34d326ff063ec4bc36ad31

clean:
	$(PYTHON) setup.py clean
	find . -type f -name "*.pyc" -exec rm {} \;

nuke: clean
	rm -rf *.egg *.egg-info env bin cover coverage.xml nosetests.xml

env virtualenv: env/bin/activate
env/bin/activate: requirements.txt setup.py
	test -d env || virtualenv --no-site-packages env
	ln -fs env/bin .
	$(PYENV) pip install -e . -r requirements.txt
	touch env/bin/activate

upgrade:
	test -d env || virtualenv --no-site-packages env
	ln -fs env/bin .
	$(PYENV) pip install -e . -r requirements.txt --upgrade
	touch env/bin/activate
