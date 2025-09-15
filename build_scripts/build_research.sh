#!/bin/bash

# Build and run Research Extractor Docker container
# This script should be run from the crawler_scripts/ directory

set -e

echo "=== Research Extractor Docker Setup ==="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory."
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
docker-compose build research-extractor

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

    # Run the container using docker-compose
    docker-compose --profile research up research-extractor

    echo ""
    echo "✅ Container execution completed!"
    echo "📝 Check the logs/ directory for any output files."
else
    echo "Container built but not run."
fi

echo ""
echo "📋 Other useful commands:"
echo "  • Run with docker-compose:    docker-compose --profile research up research-extractor"
echo "  • Run interactively:          docker-compose run --rm research-extractor /bin/bash"
echo "  • View running containers:    docker ps"
echo "  • Remove image:               docker rmi crawler_scripts-research-extractor"
