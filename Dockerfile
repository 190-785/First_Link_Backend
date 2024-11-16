# Use a slim Python image as the base
FROM python:3.11-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg2 ca-certificates \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libdbus-1-3 \
    libasound2 libnss3 libgconf-2-4 libappindicator3-1 \
    libxtst6 libatk-bridge2.0-0 libatk1.0-0 fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get -y --fix-broken install

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
