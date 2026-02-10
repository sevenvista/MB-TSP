# Docker Setup Guide

This guide provides detailed instructions for running the MB-TSP application using Docker.

## Architecture

The application consists of two main services:

1. **RabbitMQ**: Message broker for asynchronous job processing
2. **API**: FastAPI application that processes map and TSP requests

## Quick Start

```bash
# Build and start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

## Service Details

### RabbitMQ Service

- **Image**: `rabbitmq:3.12-management-alpine`
- **Ports**:
  - `5672`: AMQP protocol port
  - `15672`: Management UI
- **Credentials**: guest/guest (default)
- **Health Check**: Automatic health checking with retry logic

### API Service

- **Build**: Custom Dockerfile using Python 3.11 slim
- **Port**: `8000`
- **Dependencies**: Managed by `uv` for fast, reliable installs
- **Data Persistence**: `./data` directory mounted as volume
- **Health Check**: HTTP endpoint at `/health`

## Docker Compose Commands

### Starting Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up -d api
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop api
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f rabbitmq

# Last 100 lines
docker-compose logs --tail=100 api
```

### Rebuilding

```bash
# Rebuild images
docker-compose build

# Rebuild specific service
docker-compose build api

# Rebuild with no cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

### Service Management

```bash
# Restart services
docker-compose restart

# Restart specific service
docker-compose restart api

# Check service status
docker-compose ps

# View resource usage
docker-compose top
```

### Shell Access

```bash
# API container
docker-compose exec api /bin/sh

# RabbitMQ container
docker-compose exec rabbitmq /bin/sh

# Run one-off command
docker-compose exec api python --version
```

## Volume Management

### Data Persistence

The application uses two volumes:

1. **RabbitMQ Data**: Persists message queue data
   - Named volume: `rabbitmq_data`
   - Location: `/var/lib/rabbitmq` in container

2. **Application Data**: Persists computed map distances
   - Bind mount: `./data` → `/app/data`
   - Files: `{mapid}.json`

### Volume Commands

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect mb-tsp_rabbitmq_data

# Remove volume (when services are down)
docker volume rm mb-tsp_rabbitmq_data

# Remove all unused volumes
docker volume prune
```

## Network Configuration

The application uses a custom bridge network (`mb-tsp-network`) for service communication:

- Services communicate using service names (e.g., `rabbitmq`)
- Isolated from other Docker networks
- Automatic DNS resolution

## Environment Variables

### Using docker-compose.yml

Edit the `environment` section in `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      RABBITMQ_HOST: rabbitmq
      MAP_REQUEST_QUEUE: custom_map_queue
```

### Using .env File

Create a `.env` file in the project root:

```env
RABBITMQ_HOST=rabbitmq
MAP_REQUEST_QUEUE=map_processing_requests
```

Docker Compose will automatically load these variables.

## Health Checks

### RabbitMQ Health Check

```bash
# Check RabbitMQ status
docker-compose exec rabbitmq rabbitmq-diagnostics ping
docker-compose exec rabbitmq rabbitmq-diagnostics status
```

### API Health Check

```bash
# HTTP health endpoint
curl http://localhost:8000/health

# Check from inside container
docker-compose exec api curl http://localhost:8000/health
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check if ports are in use
lsof -i :8000
lsof -i :5672
lsof -i :15672

# Remove all containers and try again
docker-compose down -v
docker-compose up -d
```

### API Can't Connect to RabbitMQ

```bash
# Check if RabbitMQ is healthy
docker-compose ps

# Check RabbitMQ logs
docker-compose logs rabbitmq

# Verify network connectivity
docker-compose exec api ping rabbitmq

# Restart services
docker-compose restart
```

### Out of Disk Space

```bash
# Clean up unused resources
docker system prune -a

# Remove specific volumes
docker-compose down -v

# Check disk usage
docker system df
```

### Permission Issues

```bash
# Fix data directory permissions
chmod -R 755 data/

# Run container as specific user (add to docker-compose.yml)
services:
  api:
    user: "1000:1000"  # your UID:GID
```

## Production Deployment

### Security Considerations

1. **Change Default Credentials**:
```yaml
rabbitmq:
  environment:
    RABBITMQ_DEFAULT_USER: your_user
    RABBITMQ_DEFAULT_PASS: your_secure_password
```

2. **Use Secrets**:
```yaml
services:
  api:
    secrets:
      - rabbitmq_password
secrets:
  rabbitmq_password:
    file: ./secrets/rabbitmq_password.txt
```

3. **Limit Resource Usage**:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

### Performance Tuning

1. **Scale API Workers**:
```bash
docker-compose up -d --scale api=3
```

2. **Optimize RabbitMQ**:
```yaml
rabbitmq:
  environment:
    RABBITMQ_VM_MEMORY_HIGH_WATERMARK: 0.8
    RABBITMQ_DISK_FREE_LIMIT: 2GB
```

## Monitoring

### View Container Stats

```bash
docker-compose top
docker stats $(docker-compose ps -q)
```

### Export Logs

```bash
# Export to file
docker-compose logs > logs.txt

# Export specific time range
docker-compose logs --since 2024-01-01 --until 2024-01-02 > logs.txt
```

## Backup and Restore

### Backup Data

```bash
# Backup application data
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/

# Backup RabbitMQ data
docker run --rm \
  -v mb-tsp_rabbitmq_data:/data \
  -v $(pwd):/backup \
  alpine tar -czf /backup/rabbitmq-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore Data

```bash
# Restore application data
tar -xzf data-backup-20240101.tar.gz

# Restore RabbitMQ data
docker run --rm \
  -v mb-tsp_rabbitmq_data:/data \
  -v $(pwd):/backup \
  alpine tar -xzf /backup/rabbitmq-backup-20240101.tar.gz -C /
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: docker-compose build
      - name: Start services
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 10
      - name: Run tests
        run: docker-compose exec -T api python test_example.py full
      - name: Stop services
        run: docker-compose down
```
