# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    wget \
    gnupg \
    fontconfig \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libssl-dev \
    libdbus-1-3 \
    libasound2 \
    --no-install-recommends

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome.deb && \
    rm google-chrome.deb

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code to the container
COPY . /app/

# Expose the port
EXPOSE 5000

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
