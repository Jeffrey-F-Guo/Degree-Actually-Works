# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies required for web scraping and Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    gnupg2 \
    unzip \
    xvfb \
    libxi6 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    fonts-liberation \
    libappindicator3-1 \
    libnss3 \
    lsb-release \
    xdg-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY base_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r base_requirements.txt

# Copy the application code
COPY services/ ./services/


# Install Playwright browsers as the app user
RUN playwright install chromium

# Create logs directory
RUN mkdir -p /app/logs

# Expose the port the app runs on
EXPOSE 8000

# Set the default command to run the API server
CMD ["uvicorn", "services.app:app", "--host", "0.0.0.0", "--port", "8000"]