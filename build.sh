#!/bin/bash

# Log the PATH environment variable
echo "PATH is: $PATH"

echo "Downloading Google Chrome..."
mkdir -p /opt/chrome && \
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /opt/chrome/google-chrome-stable_current_amd64.deb && \
dpkg -x /opt/chrome/google-chrome-stable_current_amd64.deb /opt/chrome

echo "Setting up Chrome binary..."
export CHROME_PATH="/opt/chrome/opt/google/chrome"
export PATH="$CHROME_PATH:$PATH"

echo "Downloading Chromedriver..."
mkdir -p /opt/chromedriver && \
wget https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -O /opt/chromedriver/chromedriver.zip && \
unzip /opt/chromedriver/chromedriver.zip -d /opt/chromedriver

echo "Setting up Chromedriver binary..."
export CHROMEDRIVER_PATH="/opt/chromedriver"
export PATH="$CHROMEDRIVER_PATH:$PATH"

echo "Checking installed versions..."
"$CHROME_PATH/google-chrome" --version
"$CHROMEDRIVER_PATH/chromedriver" --version

# Clean up downloaded files to save storage space
echo "Cleaning up downloaded files..."
rm -rf /opt/chrome/google-chrome-stable_current_amd64.deb
rm -rf /opt/chromedriver/chromedriver.zip

echo "Cleanup complete!"

# Ensure dependencies are installed
echo "Installing Python dependencies..."
pip install -r requirements.txt || exit 1

# Run the application
echo "Starting the application..."
exec python app.py
