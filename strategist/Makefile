run:
	python run.py

flake:
	flake8 app tests

develop:
	pip install -e .

test:
	py.test -q -s --cov app --cov-report term-missing --tb=native
