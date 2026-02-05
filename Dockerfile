# Content Analytics Platform - Multi-stage Dockerfile
# ====================================================

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('vader_lexicon', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/models /app/logs

# =============================================================================
# API Stage - FastAPI Backend
# =============================================================================
FROM base as api

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI with Uvicorn
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Dashboard Stage - Streamlit Frontend
# =============================================================================
FROM base as dashboard

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# =============================================================================
# ETL Stage - Data Collection Worker
# =============================================================================
FROM base as etl

# Run ETL scheduler
CMD ["python", "-m", "src.etl.scheduler"]

# =============================================================================
# Development Stage - All-in-one for development
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    jupyterlab

EXPOSE 8000 8501 8888

# Default command for development
CMD ["bash"]
