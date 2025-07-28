# CERBERUS ULTIMATE - Compliant Advanced Solution
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create input/output directories
RUN mkdir -p /app/input /app/output

# Copy the compliant processing script
COPY process_compliant.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command - use compliant processor
CMD ["python", "process_compliant.py"]