# Stage 1: Build wheels
FROM python:3.12.2-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive

# Install Chromium (no driver) and build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    chromium \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY requirements.txt ./

# Build wheels to speed up runtime installs
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --no-deps --wheel-dir=/wheels -r requirements.txt

# Stage 2: Final lightweight image
FROM python:3.12.2-slim
ENV DEBIAN_FRONTEND=noninteractive

# Install only runtime Chromium
RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /wheels /wheels
# Install all Python deps from wheels
RUN pip install --no-cache-dir /wheels/*

# Copy source code
COPY . /app

# Use non-root for security
RUN useradd --create-home appuser
USER appuser

# Expose app port
EXPOSE 10000

# Launch Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]