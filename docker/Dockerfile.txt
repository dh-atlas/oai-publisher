# ===== Builder =====
FROM python:3.10-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
 && rm -rf /var/lib/apt/lists/*

# 1) requirements locali (accanto al Dockerfile) per massimizzare la cache
COPY requirements.txt /build/requirements.txt

# 2) venv + deps
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
 && /opt/venv/bin/pip install --no-cache-dir -r /build/requirements.txt

# 3) sorgente: clona da Git (opzionale). Se non passi REPO_URL rimane vuoto.
ARG REPO_URL
ARG REPO_REF=main
RUN if [ -n "$REPO_URL" ]; then git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" src; else mkdir -p src; fi

# ===== Runtime =====
FROM python:3.10-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
WORKDIR /app

RUN groupadd -r oai && useradd -r -g oai -m oai

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/src /app

RUN chown -R oai:oai /app /opt/venv /home/oai \
 && mkdir -p /home/oai/.cache/pip && chown -R oai:oai /home/oai/.cache

USER oai
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "oai-server:app"]

