#!/bin/bash

# Log the PATH environment variable
echo "PATH is: $PATH"
google-chrome --version

# Define writable directories for Chrome and Chromedriver
CHROME_DIR=/tmp/chrome
CHROMEDRIVER_DIR=/tmp/chromedriver

echo "Downloading Google Chrome..."
mkdir -p $CHROME_DIR && \
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O $CHROME_DIR/google-chrome-stable_current_amd64.deb && \
dpkg -x $CHROME_DIR/google-chrome-stable_current_amd64.deb $CHROME_DIR

echo "Setting up Chrome binary..."
export CHROME_PATH="$CHROME_DIR/opt/google/chrome"
export PATH="$CHROME_PATH:$PATH"

echo "Downloading Chromedriver..."
mkdir -p $CHROMEDRIVER_DIR && \
wget https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -O $CHROMEDRIVER_DIR/chromedriver.zip && \
unzip $CHROMEDRIVER_DIR/chromedriver.zip -d $CHROMEDRIVER_DIR

echo "Setting up Chromedriver binary..."
export CHROMEDRIVER_PATH="$CHROMEDRIVER_DIR"
export PATH="$CHROMEDRIVER_PATH:$PATH"

echo "Checking installed versions..."
"$CHROME_PATH/google-chrome" --version
"$CHROMEDRIVER_PATH/chromedriver" --version

# Clean up downloaded files to save storage space
echo "Cleaning up downloaded files..."
rm -rf $CHROME_DIR/google-chrome-stable_current_amd64.deb
rm -rf $CHROMEDRIVER_DIR/chromedriver.zip

echo "Cleanup complete!"

# Ensure dependencies are installed from requirements.txt
echo "Installing Python dependencies..."
pip install -r requirements.txt || exit 1

# # Run the application with gunicorn
# echo "Starting the application with gunicorn..."
# exec gunicorn app:app --bind 0.0.0.0:$PORT