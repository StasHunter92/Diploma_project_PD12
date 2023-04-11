FROM python:3.10-slim

WORKDIR /todolist

ENV PYTHONUNBUFFERED=1

RUN pip install poetry

COPY pyproject.toml .
COPY core/. ./core
COPY goals/. ./goals
COPY diploma_project_pd12/. ./diploma_project_pd12
# COPY .env /todolist/.env
COPY manage.py .
COPY README.MD ./README.md

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root
# RUN python manage.py collectstatic -c --no-input
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
