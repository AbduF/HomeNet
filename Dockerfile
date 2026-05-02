# ===== HomeNet 2026 - Multi-stage Production Build =====
# Build with: docker build -t homenet:2026 .
# Run with: docker run -d -p 5000:5000 --name homenet --restart unless-stopped \
#           -v homenet-data:/app/data homenet:2026

# ---- Stage 1: Builder ----
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim-bookworm

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsmasq arp-scan iptables ufw curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/dnsmasq.d /var/log/homenet

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd -m -u 1000 -G sudo homenet && \
    mkdir -p /app/data /app/static/icons && \
    chown -R homenet:homenet /app /var/log/homenet /etc/dnsmasq.d

WORKDIR /app

# Copy application files
COPY --chown=homenet:homenet . .

# Copy pre-built static assets (icons for PWA)
COPY --chown=homenet:homenet static/icons/ /app/static/icons/

# Health check for orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Use gunicorn for production
USER homenet
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]