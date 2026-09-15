FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

COPY app.py config.py ./
COPY src ./src
COPY static ./static
COPY config ./config

RUN mkdir -p /app/data \
    && useradd --create-home --uid 10001 lentswe \
    && chown -R lentswe:lentswe /app

USER lentswe
ENV PYTHONUNBUFFERED=1 \
    LENTSWE_DATA_DIR=/app/data \
    LENTSWE_HOST=0.0.0.0 \
    PORT=7000 \
    LOG_LEVEL=INFO \
    FLASK_DEBUG=0

EXPOSE 7000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:7000/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "--workers", "2", "--threads", "2", "app:app"]
