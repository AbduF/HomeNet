# HomeNet Dockerfile for Raspberry Pi 3 (ARMv7)
# Build with: docker build -t homenet .
# Run with: docker run -d -p 5000:5000 --name homenet --restart unless-stopped homenet

# Use official Python image for ARMv7 (Raspberry Pi 3)
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsmasq \
    arp-scan \
    iptables \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx \
    speedtest-cli \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create static and tmp directories
RUN mkdir -p static/css static/js tmp

# Copy static files
COPY static/css/style.css static/css/
COPY static/js/chart.js static/js/

# Expose port 5000
EXPOSE 5000

# Set up entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the application
ENTRYPOINT ["/entrypoint.sh"]