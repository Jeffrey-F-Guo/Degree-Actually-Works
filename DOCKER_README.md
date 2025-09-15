# Multi-Service Docker Setup

This repository now supports multiple Docker services with a clean, organized structure.

## Directory Structure

```
crawler_scripts/
├── docker/
│   ├── research-extractor/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── llm-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app.py
│   └── courses-extractor/
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
├── build_scripts/
│   ├── build_all.sh
│   ├── build_research.sh
│   ├── build_llm.sh
│   └── build_courses.sh
└── [existing scripts and utils]
```

## Services

### 1. Research Extractor (`research-extractor`)
- **Purpose**: Extracts research information from web sources
- **Profile**: `research`
- **Type**: One-time execution (scraping job)
- **Dependencies**: crawl4ai, playwright, langchain

### 2. LLM Service (`llm-service`)
- **Purpose**: Provides LLM API endpoints for text generation and processing
- **Profile**: `llm`
- **Type**: Long-running service
- **Port**: 8000
- **Dependencies**: fastapi, uvicorn, langchain

### 3. Courses Extractor (`courses-extractor`)
- **Purpose**: Extracts course information from web sources
- **Profile**: `courses`
- **Type**: One-time execution (scraping job)
- **Dependencies**: crawl4ai, playwright, langchain

## Usage

### Building Services

#### Build All Services
```bash
# Using build script
./build_scripts/build_all.sh

# Using docker-compose
docker-compose build
```

#### Build Individual Services
```bash
# Research extractor
./build_scripts/build_research.sh
# or
docker-compose build research-extractor

# LLM service
./build_scripts/build_llm.sh
# or
docker-compose build llm-service

# Courses extractor
./build_scripts/build_courses.sh
# or
docker-compose build courses-extractor
```

### Running Services

#### Run Individual Services
```bash
# Research extractor (one-time run)
docker-compose --profile research up research-extractor

# LLM service (long-running)
docker-compose --profile llm up llm-service

# Courses extractor (one-time run)
docker-compose --profile courses up courses-extractor
```

#### Run Multiple Services
```bash
# Run LLM service and research extractor
docker-compose --profile llm --profile research up

# Run all services
docker-compose --profile research --profile llm --profile courses up
```

#### Run LLM Service in Background
```bash
docker-compose --profile llm up -d llm-service
```

### LLM Service API

When the LLM service is running, it provides the following endpoints:

- **Health Check**: `GET /health`
- **Root**: `GET /`
- **Generate Text**: `POST /generate`
- **Summarize Text**: `POST /summarize`
- **API Documentation**: `GET /docs` (Swagger UI)

#### Example API Usage
```bash
# Health check
curl http://localhost:8000/health

# Generate text
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, world!", "model": "gemini-pro"}'

# Summarize text
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Long text to summarize...", "model": "gemini-pro"}'
```

## Environment Variables

Create a `.env` file in the root directory for environment variables:

```env
# LLM Service
API_KEY=your_api_key_here

# Other environment variables as needed
```

## Docker Profiles

Docker Compose profiles allow you to run specific combinations of services:

- `research`: Research extractor service
- `llm`: LLM API service
- `courses`: Courses extractor service

## Development

### Adding a New Service

1. Create a new directory under `docker/`:
   ```bash
   mkdir docker/new-service
   ```

2. Create `Dockerfile` and `requirements.txt` in the new directory

3. Add the service to `docker-compose.yml`:
   ```yaml
   new-service:
     build:
       context: .
       dockerfile: docker/new-service/Dockerfile
     container_name: new-service
     restart: unless-stopped
     profiles:
       - new-service
   ```

4. Create a build script in `build_scripts/build_new_service.sh`

### Modifying Existing Services

- **Dependencies**: Update the `requirements.txt` in the service directory
- **Code**: The services mount the actual script directories as volumes
- **Configuration**: Update the service definition in `docker-compose.yml`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure port 8000 is not in use by another service
2. **Permission issues**: Ensure the build scripts are executable (`chmod +x build_scripts/*.sh`)
3. **Volume mounting**: Check that the source directories exist and are accessible

### Useful Commands

```bash
# View running containers
docker ps

# View logs
docker-compose logs [service-name]

# Stop all services
docker-compose down

# Remove all images
docker-compose down --rmi all

# Run service interactively
docker-compose run --rm [service-name] /bin/bash
```

## Migration from Single Dockerfile

If you were using the original single `Dockerfile`, you can still use it by:

1. Renaming it to `docker/research-extractor/Dockerfile`
2. Updating the build context in `docker-compose.yml`
3. Using the new build scripts

The new structure provides better organization and allows for independent service development and deployment.
