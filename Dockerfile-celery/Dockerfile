# Dockerfile for Celery Worker

FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && apt-get clean
    
# Install dependencies
COPY backend/requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ /app/

# Set environment variables (these will be overridden by Azure)
ENV OPENAI_API_KEY=""
ENV REDIS_URL=""

# Run Celery worker
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
