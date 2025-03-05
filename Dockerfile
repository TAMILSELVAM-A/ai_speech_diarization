# Use an official Python runtime as a parent image
FROM python:3.8-alphine

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (Alpine uses apk)
RUN apk add --no-cache \
    build-base \
    ffmpeg \
    libsndfile

# Copy only requirements first to leverage Docker caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project after installing dependencies
COPY . .

# Expose the port that Cloud Run will use
EXPOSE 8000

# Ensure Cloud Run provides the PORT dynamically
ENV PORT 8000

# Start the application with proper port binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
