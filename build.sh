#!/bin/bash

# Log the PATH environment variable
echo "PATH is: $PATH"

# Check if Chrome is installed
echo "Checking for Google Chrome..."
which google-chrome || echo "Google Chrome not found"

# Log Chrome version
google-chrome --version || echo "Google Chrome version not found"

# Check if Chromedriver is installed
echo "Checking for Chromedriver..."
which chromedriver || echo "Chromedriver not found"

# Log Chromedriver version
chromedriver --version || echo "Chromedriver version not found"

# Install Chrome if not found
if ! which google-chrome; then
    echo "Installing Google Chrome..."
    apt-get update && apt-get install -y wget unzip
    wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install -y /tmp/google-chrome.deb || echo "Failed to install Chrome"
fi

# Ensure dependencies are installed
echo "Installing Python dependencies..."
pip install -r requirements.txt || exit 1

# Run the application
echo "Starting the application..."
exec python app.py
