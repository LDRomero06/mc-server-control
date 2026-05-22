# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (e.g., curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run as a non-privileged user for security
#RUN useradd -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# Expose backend port
EXPOSE 5000

# Start application (adjust 'app:app' to match your WSGI/ASGI file and variable name)
CMD ["python", "app.py"]
