FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

# Non-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]