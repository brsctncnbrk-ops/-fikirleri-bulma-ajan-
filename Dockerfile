FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install the application package (src layout)
COPY pyproject.toml ./
COPY src ./src
RUN pip install .

# Persist SQLite under a mountable volume by default
ENV DATABASE_PATH=/app/data/trendidea.db
RUN mkdir -p /app/data

CMD ["python", "-m", "trendidea.main"]
