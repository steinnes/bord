black:
	poetry run black $(shell git diff --name-only HEAD|grep \.py$)
