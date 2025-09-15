# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies required for web scraping
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
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the courses_extractor folder contents
COPY ../../scripts/Gemini/courses_extractor/ ./

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Install Playwright browsers as the app user
RUN playwright install chromium

# Set the default command to run the courses crawler
CMD ["python", "course_crawler.py"]
