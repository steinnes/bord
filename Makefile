black:
	poetry run black $(shell git diff --name-only HEAD|grep \.py$)

lint:
	poetry run flake8 bord/

run:
	poetry run python app.py
