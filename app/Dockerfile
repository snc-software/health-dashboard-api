# syntax=docker/dockerfile:1

# ---------- builder ----------
FROM python:3.14-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.lock ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.lock

COPY pyproject.toml ./
COPY health_dashboard_service ./health_dashboard_service
RUN /opt/venv/bin/pip install --no-cache-dir --no-deps .

# ---------- runtime ----------
FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --no-create-home app

COPY --from=builder /opt/venv /opt/venv

WORKDIR /srv
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"

CMD ["uvicorn", "health_dashboard_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
