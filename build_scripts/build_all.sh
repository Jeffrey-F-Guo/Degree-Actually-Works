#!/bin/bash

# Build all Docker services
# This script should be run from the crawler_scripts/ directory

set -e

echo "=== Building All Docker Services ==="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory."
    echo "Please run this script from the crawler_scripts/ directory."
    exit 1
fi

echo "🔨 Building all services..."

# Build research extractor
echo "Building research-extractor..."
docker-compose build research-extractor

# Build LLM service
echo "Building llm-service..."
docker-compose build llm-service

# Build courses extractor
echo "Building courses-extractor..."
docker-compose build courses-extractor

echo ""
echo "✅ All services built successfully!"
echo ""
echo "📋 Available commands:"
echo "  • Run research extractor:     docker-compose --profile research up research-extractor"
echo "  • Run LLM service:            docker-compose --profile llm up llm-service"
echo "  • Run courses extractor:      docker-compose --profile courses up courses-extractor"
echo "  • Run all services:           docker-compose --profile research --profile llm --profile courses up"
echo "  • Run LLM service only:       docker-compose up llm-service"
echo ""
echo "🔍 To check running containers: docker ps"
echo "🗑️  To remove all images:       docker-compose down --rmi all"
