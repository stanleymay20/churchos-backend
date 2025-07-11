# CHURCHOS™ Backend Docker Configuration
# Production-ready sacred operating system backend

# Use Python 3.11 slim image for optimal performance
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create sacred logs directory
RUN mkdir -p /app/logs

# Copy sacred application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' churchos \
    && chown -R churchos:churchos /app
USER churchos

# Expose sacred port
EXPOSE 8000

# Health check for sacred monitoring
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Sacred startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 