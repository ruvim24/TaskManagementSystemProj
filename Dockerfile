#FROM python:3.12
#
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#ENV PIP_DEFAULT_TIMEOUT=300
#
#RUN pip install poetry
#
#WORKDIR /app
#
#COPY . .
#
#RUN poetry install --no-root
#
#CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


## Imaginea de bază cu Python
#FROM python:3.12-slim
#
## Setează variabilele de mediu
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#
## Instalează Poetry
#RUN pip install poetry
#
## Creează un utilizator non-root
#RUN addgroup --gid 1000 appgroup && adduser --system --uid 1000 --ingroup appgroup appuser
#
## Setează directorul de lucru
#WORKDIR /app
#
## Copiază fișierele de configurare Poetry
#COPY pyproject.toml poetry.lock ./
#
## Dă permisiuni de scriere utilizatorului nou creat
#RUN chown -R appuser:appgroup /app
#RUN chmod -R 775 /app
#
## Comută la utilizatorul non-root
#USER appuser
#
## Instalează dependințele (acum cu permisiunile corecte)
#RUN poetry install --no-root
#
## Copiază restul codului aplicației
#COPY --chown=appuser:appgroup . /app