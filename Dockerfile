# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies required for crawl4ai and web scraping
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

# Copy requirements file from the root
COPY base_requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the research_extractor folder contents
COPY scripts/Gemini/research_extractor/ ./

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Install Playwright browsers as the app user (so they go to the right cache location)
RUN playwright install chromium

# Set the default command to run the research crawler
CMD ["python", "research_crawler.py"]