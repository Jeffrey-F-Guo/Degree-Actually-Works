#!/bin/bash

# Build and run LLM Service Docker container
# This script should be run from the crawler_scripts/ directory

set -e

echo "=== LLM Service Docker Setup ==="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory."
    echo "Please run this script from the crawler_scripts/ directory."
    exit 1
fi

if [ ! -d "utils" ]; then
    echo "❌ Error: utils/ directory not found."
    echo "Please check your directory structure."
    exit 1
fi

echo "✅ Directory structure verified"
echo ""

echo "🔨 Building LLM Service Docker image..."
docker-compose build llm-service

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi

echo ""

# Ask user if they want to run the container
read -p "Do you want to run the LLM service now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Running LLM Service..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Run the container using docker-compose
    docker-compose --profile llm up llm-service

    echo ""
    echo "✅ LLM Service is running!"
    echo "🌐 Service available at: http://localhost:8000"
    echo "📚 API docs available at: http://localhost:8000/docs"
else
    echo "Container built but not run."
fi

echo ""
echo "📋 Other useful commands:"
echo "  • Run with docker-compose:    docker-compose --profile llm up llm-service"
echo "  • Run in background:          docker-compose --profile llm up -d llm-service"
echo "  • Run interactively:          docker-compose run --rm llm-service /bin/bash"
echo "  • View logs:                  docker-compose logs llm-service"
echo "  • Stop service:               docker-compose down"
echo "  • View running containers:    docker ps"
