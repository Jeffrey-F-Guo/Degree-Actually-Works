#!/bin/bash

# Build and run Courses Extractor Docker container
# This script should be run from the crawler_scripts/ directory

set -e

echo "=== Courses Extractor Docker Setup ==="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory."
    echo "Please run this script from the crawler_scripts/ directory."
    exit 1
fi

if [ ! -d "scripts/Gemini/courses_extractor" ]; then
    echo "❌ Error: scripts/Gemini/courses_extractor/ directory not found."
    echo "Please check your directory structure."
    exit 1
fi

echo "✅ Directory structure verified"
echo ""

echo "🔨 Building Courses Extractor Docker image..."
docker-compose build courses-extractor

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
    echo "🚀 Running Courses Extractor..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Run the container using docker-compose
    docker-compose --profile courses up courses-extractor

    echo ""
    echo "✅ Container execution completed!"
    echo "📝 Check the logs/ directory for any output files."
else
    echo "Container built but not run."
fi

echo ""
echo "📋 Other useful commands:"
echo "  • Run with docker-compose:    docker-compose --profile courses up courses-extractor"
echo "  • Run interactively:          docker-compose run --rm courses-extractor /bin/bash"
echo "  • View running containers:    docker ps"
echo "  • Remove image:               docker rmi crawler_scripts-courses-extractor"
