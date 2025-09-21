# WWU Resource Extractor API - Deployment Guide

## Overview
This is a FastAPI application that scrapes WWU resources (research, courses, events) and provides them via REST API endpoints. The application is containerized using Docker for easy deployment and consistent environments.

## Prerequisites
- Docker and Docker Compose installed on the server
- Tailscale access to the server

## Quick Deployment

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd crawler_scripts
```

### 2. Build and Run with Docker Compose
```bash
# Build and start the service
docker-compose up --build -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# Test an endpoint
curl http://localhost:8000/extract/research/CSCI
```

## API Endpoints

### Health Check
- **GET** `/health` - Check if the API is running

### Research Extraction
- **GET** `/extract/research/{department_code}` - Extract faculty research for a department
  - Example: `/extract/research/CSCI`

### Events Extraction
- **GET** `/extract/events` - Extract all events from WWU

### Courses Extraction
- **GET** `/extract/courses/{department_code}` - Extract courses for a department
  - Example: `/extract/courses/CSCI`

### Bulk Extraction
- **GET** `/extract/all` - Extract all data from all sources

## Accessing the API

Once deployed, the API will be available at:
- **Local**: `http://localhost:8000`
- **Tailscale**: `http://[tailscale-ip]:8000`

## Management Commands

### Start/Stop/Restart
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild and restart (after code changes)
docker-compose up --build -d
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Logs for specific service
docker-compose logs wwu-extractor-api
```

### Update the Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs wwu-extractor-api

# Check if port 8000 is available
netstat -tulpn | grep 8000
```

### API Not Responding
```bash
# Check container status
docker-compose ps

# Check health endpoint
curl http://localhost:8000/health

# Restart container
docker-compose restart
```

### Permission Issues
```bash
# Check logs directory permissions
ls -la logs/

# Fix permissions if needed
sudo chown -R $USER:$USER logs/
```

## Data Output

The API extracts data and saves it to CSV files in the `logs/` directory (mounted as a volume):
- `research_CSCI.csv` - Computer Science research data
- `research_MATH.csv` - Mathematics research data
- `events.csv` - University events
- `CSCI_courses.csv` - Computer Science courses
- `MATH_courses.csv` - Mathematics courses

**Note**: The `logs/` directory is mounted as a volume, so data persists even when the container is restarted.

## Security Notes

- The container runs as a non-root user for security
- No sensitive data is exposed in the API responses
- All scraping is done from within the container
- Logs are stored locally and not transmitted externally

## Performance

- The API includes timeout handling (5-10 minutes for large extractions)
- Health checks ensure the service is responsive
- Container automatically restarts if it crashes
- Memory usage is optimized for the scraping workload
