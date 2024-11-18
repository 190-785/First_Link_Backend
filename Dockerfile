# Use a lightweight Python image
FROM python:3.10-slim

# Install build tools and Rust (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    cargo \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port and run the app
EXPOSE 10000
CMD ["python", "app.py"]
