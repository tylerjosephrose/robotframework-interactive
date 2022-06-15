clean:
	rm -rf build
	rm -rf dist

build:
	python setup.py sdist
	python setup.py bdist_wheel

upload_test:
	python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	python -m twine upload dist/*
