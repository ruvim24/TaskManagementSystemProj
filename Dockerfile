FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=300

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --only main

COPY . .

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

