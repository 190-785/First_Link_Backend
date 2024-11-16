# === Stage 1: Build Environment ===
FROM python:3.11-slim AS build

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    CHROME_DEB=google-chrome.deb

# Install system dependencies for building and running
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libssl-dev \
    libdbus-1-3 \
    libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Chrome and clean up unnecessary files
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o $CHROME_DEB && \
    apt-get install -y ./$CHROME_DEB && rm -f $CHROME_DEB

# Install Python dependencies
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromedriver Autoinstaller
RUN pip install --no-cache-dir chromedriver-autoinstaller

# === Stage 2: Runtime Environment ===
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libssl-dev \
    libdbus-1-3 \
    libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Chrome and Python dependencies from build stage
COPY --from=build /usr/bin/google-chrome /usr/bin/google-chrome
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the Flask app code
WORKDIR /app
COPY . /app/

# Expose the Flask port
EXPOSE 5000

# Healthcheck to ensure the server is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD curl -f http://localhost:5000/api || exit 1

# Run the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
