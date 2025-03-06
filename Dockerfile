# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies in a temporary directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set the PORT environment variable
ENV PORT=8000
EXPOSE $PORT

# Copy the rest of the application
COPY . .

# Start the application
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
