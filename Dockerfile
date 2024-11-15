# Use the official Python image as a base image
FROM python:3.11-slim

# Install necessary dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    unzip \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libx11-dev \
    libxcomposite-dev \
    libxrandr-dev \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libxcb1 \
    libxss1 \
    libappindicator3-1 \
    libnspr4 \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    xdg-utils \
    libfontconfig1

# Download and install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb && \
    apt-get -y install -f

# Install chromedriver
RUN LATEST=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Set display port to avoid crashes in headless mode
ENV DISPLAY=:99

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the container
COPY . /app

# Expose port 5000
EXPOSE 5000

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
