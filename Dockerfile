FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=300

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* /app/

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]