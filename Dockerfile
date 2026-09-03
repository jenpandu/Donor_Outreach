# --- Build stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --prefix=/install .

# --- Final stage ---
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/ src/
COPY migrations/ migrations/

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["sh", "-c", "flask --app donor_outreach.app db upgrade && gunicorn --bind 0.0.0.0:5000 'donor_outreach.app:create_app()'"]