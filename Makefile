all: install dev test

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

test:
	pytest -v password_rotate/tests
