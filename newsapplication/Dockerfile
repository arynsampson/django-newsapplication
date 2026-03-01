# Use official Python image
FROM python:3.12-slim

# Prevent Python from writing pyc files and enable stdout/stderr flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    libssl-dev \
    libffi-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Make it executable
RUN chmod +x /app/entrypoint.sh

# Expose Django port
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]