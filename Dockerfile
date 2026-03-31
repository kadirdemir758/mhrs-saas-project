# syntax=docker/dockerfile:1
# ════════════════════════════════════════════════
#  MHRS SaaS — Dockerfile
#  Multi-stage build for production-ready image
# ════════════════════════════════════════════════

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into /build/deps
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Stage 2: Runtime Image ───────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# System runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages

# Copy application source
COPY . .

# Non-root user for security
RUN addgroup --system mhrs && adduser --system --ingroup mhrs mhrs
RUN chown -R mhrs:mhrs /app
USER mhrs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
