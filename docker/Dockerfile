# Start from AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for Chromium
RUN yum install -y \
    libX11 \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    xorg-x11-server-Xvfb \
    nss \
    && yum clean all

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies (crawl4ai + dotenv + pydantic + prettytable)
COPY base_requirements.txt .
RUN pip install -r base_requirements.txt

# Run crawl4ai setup to install playwright + browsers
RUN crawl4ai-setup

# Copy your app code
COPY scripts/Gemini/research_extractor/ ${LAMBDA_TASK_ROOT}

# Set Lambda handler
CMD ["app.lambda_handler"]
