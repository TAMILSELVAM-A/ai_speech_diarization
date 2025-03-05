# Use a non-Alpine Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (Debian-based)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project after installing dependencies
COPY . .

# Expose the port that Cloud Run will use
EXPOSE 8000

# Ensure Cloud Run provides the PORT dynamically
ENV PORT 8000

# Start the application with proper port binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
