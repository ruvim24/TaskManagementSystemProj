#!/bin/sh
poetry run ruff check .
poetry run python manage.py test apps.tasks.tests
