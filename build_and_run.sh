#!/bin/bash

# Build and run script for Research Extractor Docker container
# This script should be run from the crawler_scripts/ directory

set -e

echo "=== Research Extractor Docker Setup ==="
echo ""

# Check if we're in the right directory
if [ ! -f "base_requirements.txt" ]; then
    echo "❌ Error: base_requirements.txt not found in current directory."
    echo "Please run this script from the crawler_scripts/ directory."
    exit 1
fi

if [ ! -d "scripts/Gemini/research_extractor" ]; then
    echo "❌ Error: scripts/Gemini/research_extractor/ directory not found."
    echo "Please check your directory structure."
    exit 1
fi

echo "✅ Directory structure verified"
echo ""

echo "🔨 Building Research Extractor Docker image..."
docker build -t research-extractor:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi

echo ""

# Ask user if they want to run the container
read -p "Do you want to run the container now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Running Research Extractor..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Run the container
    docker run --rm \
        --name research-extractor-run \
        -v "$(pwd)/logs:/app/logs" \
        research-extractor:latest

    echo ""
    echo "✅ Container execution completed!"
    echo "📝 Check the logs/ directory for any output files."
else
    echo "Container built but not run."
fi

echo ""
echo "📋 Other useful commands:"
echo "  • Run container:           docker run --rm research-extractor:latest"
echo "  • Run interactively:       docker run -it --rm research-extractor:latest /bin/bash"
echo "  • Use docker-compose:      docker-compose up --build"
echo "  • View running containers: docker ps"
echo "  • Remove image:            docker rmi research-extractor:latest"