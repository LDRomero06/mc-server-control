FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (NOT .env)
COPY . .

# Copy .env file at runtime via volume mount, not COPY

# Expose port for backend
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
