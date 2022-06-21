clean:
	rm -rf build
	rm -rf dist
	rm -rf robotframeworkinteractive.egg-info

build:
	python -m unittest discover tests
	python setup.py sdist
	python setup.py bdist_wheel

upload_test:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*
