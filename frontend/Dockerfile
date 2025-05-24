FROM python:3.12.6-slim

# Install poetry
RUN pip install --upgrade pip \
 && pip install poetry

WORKDIR /app

# Copy the project files including pyproject.toml
COPY pyproject.toml poetry.lock* ./
COPY frontend/ ./frontend/
COPY src/ ./src/

# Install dependencies (frontend will use shared env)
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

EXPOSE 8501

CMD ["streamlit", "run", "frontend/streamlit_frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
