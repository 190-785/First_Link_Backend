# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and to force UTF-8 encoding
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

# Install system dependencies for running Chrome
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
    apt install ./google-chrome.deb && \
    rm google-chrome.deb

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code to the container
COPY . /app

# Expose the port that Flask will run on
EXPOSE 5000

# # Command to run the app with Gunicorn
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
