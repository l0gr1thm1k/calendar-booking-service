FROM python:3.12.6

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml /app/

COPY poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --only main --no-root

COPY src /app/

EXPOSE 7100

CMD ["python", "application.py"]