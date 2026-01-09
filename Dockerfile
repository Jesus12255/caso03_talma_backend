# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for some python packages like cv2/pillow if using non-binary)
# libgl1-mesa-glx might be needed for opencv if not using headless, but keeping it minimal for now.
# We install curl for healthchecks if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command to run the API (can be overridden for Celery)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
