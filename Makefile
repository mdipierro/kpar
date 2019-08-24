.PHONY: clean build install test deploy
clean:
	rm dist/* | echo ''
	find . -name '*.pyc' -delete
	find . -name '*~' -delete
	find . -name '#*' -delete
	python3 setup.py clean
build:	clean
	python3 setup.py clean
	python3 setup.py build
test: build
	python3 -m pip install -r requirements.txt
	python3 -m pytest --cov=kpar -v -s tests/
install: build
	python3 setup.py install
deploy:
	#http://guide.python-distribute.org/creation.html
	python3 setup.py sdist
	twine upload dist/*
