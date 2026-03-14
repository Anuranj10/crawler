# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# tesseract-ocr is required for our document processing (Phase 8)
# libgl1 is required by OpenCV/Pillow in some environments
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (FastAPI defaults to 8000)
EXPOSE 8000

# Specify how to run the container (default command)
# Using uvicorn to serve the API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
