# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim AS builder

# Set environment variables for cleaner logs and isolated dependencies
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENV=/opt/venv

# Set the working directory
WORKDIR /app

# Install system dependencies (Debian-based)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy only the requirements file to install dependencies first (caching layer)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Build Final Image ----
FROM python:3.11-slim

# Set environment variables for runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application files
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000 

# Start the application with proper port binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
