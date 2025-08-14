FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install --no-root

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
