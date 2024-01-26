all: install dev test

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

test:
	pytest password_rotate/tests
