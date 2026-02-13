# Map Processing and TSP API

A FastAPI server with RabbitMQ integration for map processing using A* pathfinding and solving the Traveling Salesman Problem (TSP).

## Features

- **Map Processing Endpoint**: Accepts a 2D grid map and calculates distances between all SHELFs, START to SHELFs, and SHELFs to END using A* pathfinding with multithreading
- **TSP Solver Endpoint**: Solves the Traveling Salesman Problem based on pre-computed distances
- **RabbitMQ Integration**: Asynchronous message processing with separate request and response queues
- **Persistent Storage**: Computed distances are stored locally for reuse

## Architecture

### Data Types

- **EType**: OBSTACLE, PATH, START, END, SHELF
- **Cell**: {type: EType, id: string | null}
  - `id` is optional for PATH and OBSTACLE cells (auto-generated if null)
  - `id` is required for START, END, and SHELF cells (used for routing)
- **Map**: 2D array of Cells

### Endpoints

#### 1. Map Processing (Queue: `map_processing_requests`)

**Input:**
```json
{
  "map": [[{"type": "START", "id": "s1"}, {"type": "PATH", "id": "p1"}], ...],
  "mapid": "map123"
}
```

**Output (Queue: `map_processing_responses`):**
```json
{
  "jobid": "uuid",
  "status": "complete|error",
  "errormessage": "optional error message"
}
```

**Process:**
- Calculates distances between:
  - All SHELF to SHELF pairs
  - All START to SHELF pairs
  - All SHELF to END pairs
- Uses multithreading for parallel computation
- Stores results in `data/{mapid}.json`

#### 2. TSP Solver (Queue: `tsp_requests`)

**Input:**
```json
{
  "jobid": "uuid",
  "mapid": "map123",
  "point_of_interest": ["shelf1", "shelf2", "shelf3"]
}
```

**Output (Queue: `tsp_responses`):**
```json
{
  "point_of_interest": ["shelf1", "shelf3", "shelf2"],
  "jobid": "uuid",
  "status": "complete|error",
  "errormessage": "optional error message"
}
```

**Process:**
- Loads pre-computed distances from `data/{mapid}.json`
- Solves TSP using brute force (≤10 points) or nearest neighbor heuristic (>10 points)
- Returns optimal visiting order

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ and uv (for local development)
- OR Python 3.11+ and RabbitMQ installed locally

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker Compose, which will start both the API and RabbitMQ:

```bash
# Build and start all services
docker-compose up -d

# Or use the Makefile
make up
```

That's it! The API will be available at `http://localhost:8000` and RabbitMQ management UI at `http://localhost:15672`

### Option 1b: Pre-built image from GHCR

When this repo is on GitHub, the API image is published to [GitHub Container Registry (ghcr.io)](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) on every push or merge to `main`.

Replace `OWNER/REPO` with your GitHub org/repo (e.g. `edwardwong/MB-TSP`):

```yaml
# docker-compose.yml - use published image instead of building
services:
  api:
    image: ghcr.io/OWNER/REPO:latest
    # ... same env, ports, volumes as in docker-compose.yml
```

Pull and run:

```bash
docker pull ghcr.io/OWNER/REPO:latest
```

Tags: `latest` (main), `main`, and the git SHA.

### Option 2: Local Development with uv

1. Install uv (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

2. Install dependencies:
```bash
# Sync dependencies from pyproject.toml
uv sync

# Or use the Makefile
make install
```

3. Start RabbitMQ:
```bash
# macOS
brew install rabbitmq
brew services start rabbitmq

# Or using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

4. Run the application:
```bash
# Run the application
uv run python main.py

# Or with hot reload for development
uv run uvicorn main:app --reload

# Or use the Makefile
make run      # Production mode
make dev      # Development mode with hot reload
```

## Configuration

Environment variables:
- `RABBITMQ_HOST`: RabbitMQ server host (default: `localhost`)
- `MAP_REQUEST_QUEUE`: Map processing request queue (default: `map_processing_requests`)
- `MAP_RESPONSE_QUEUE`: Map processing response queue (default: `map_processing_responses`)
- `TSP_REQUEST_QUEUE`: TSP request queue (default: `tsp_requests`)
- `TSP_RESPONSE_QUEUE`: TSP response queue (default: `tsp_responses`)

## Usage

### Using Docker Compose (Recommended)

```bash
# Start all services
make up
# or
docker-compose up -d

# View logs
make logs
# or
docker-compose logs -f

# Stop services
make down
# or
docker-compose down
```

### Using Local Development

```bash
# Make sure RabbitMQ is running first
make dev
# or
uv run python main.py
```

The server will start on `http://localhost:8000`

### Quick Commands with Makefile

```bash
make help           # Show all available commands
make up             # Start all services
make down           # Stop all services
make logs           # View logs
make logs-api       # View API logs only
make restart        # Restart all services
make clean          # Clean up everything
make test-map       # Send test map request
make test-tsp       # Send test TSP request
make test-consume   # Consume responses
make test-full      # Run full test
```

### Send messages to RabbitMQ:

**Example: Map Processing Request**
```python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

request = {
    "map": [
        [
            {"type": "START", "id": "start1"},
            {"type": "PATH", "id": null},  # IDs are optional for PATH
            {"type": "SHELF", "id": "shelf1"}
        ],
        [
            {"type": "PATH", "id": null},
            {"type": "OBSTACLE", "id": null},  # IDs are optional for OBSTACLE
            {"type": "SHELF", "id": "shelf2"}
        ],
        [
            {"type": "SHELF", "id": "shelf3"},
            {"type": "PATH", "id": null},
            {"type": "END", "id": "end1"}
        ]
    ],
    "mapid": "warehouse_1"
}

channel.basic_publish(
    exchange='',
    routing_key='map_processing_requests',
    body=json.dumps(request)
)

connection.close()
```

**Example: TSP Request**
```python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

request = {
    "jobid": "job123",
    "mapid": "warehouse_1",
    "point_of_interest": ["shelf1", "shelf2", "shelf3"]
}

channel.basic_publish(
    exchange='',
    routing_key='tsp_requests',
    body=json.dumps(request)
)

connection.close()
```

### Consume responses:

```python
import pika

def callback(ch, method, properties, body):
    print(f"Received: {body}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Listen to map processing responses
channel.basic_consume(
    queue='map_processing_responses',
    on_message_callback=callback,
    auto_ack=True
)

# Or listen to TSP responses
channel.basic_consume(
    queue='tsp_responses',
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
```

## API Endpoints

- `GET /`: Service status and queue information
- `GET /health`: Health check endpoint

## Data Storage

Computed distances are stored in the `data/` directory with the filename pattern: `{mapid}.json`

Example structure:
```json
[
  {
    "from_id": "shelf1",
    "to_id": "shelf2",
    "distance": 5
  },
  {
    "from_id": "start1",
    "to_id": "shelf1",
    "distance": 3
  }
]
```

## Algorithms

### A* Pathfinding
- Uses Manhattan distance heuristic
- 4-directional movement (up, down, left, right)
- Avoids OBSTACLE cells
- Returns shortest path distance or -1 if no path exists

### TSP Solver

Modern heuristic algorithms based on research from [Travelling Salesman Problem - Wikipedia](https://en.wikipedia.org/wiki/Travelling_salesman_problem):

- **Very Small (≤7 points)**: Brute force enumeration for optimal solution
- **Small (8-10 points)**: Nearest neighbor + 2-opt improvement
- **Medium/Large (>10 points)**: Multi-start nearest neighbor + 2-opt + 3-opt optimization

#### Quick Overview

| Algorithm | Description | Quality |
|-----------|-------------|---------|
| Nearest Neighbor | Greedy constructive heuristic | Fast initial solution |
| 2-opt | Pairwise edge exchange | ~5% from optimal |
| 3-opt | Triple edge exchange | ~2% from optimal |
| Multi-start | Try multiple starting points | Best of several runs |

**Performance:** Solutions typically within 2-5% of optimal, computed in milliseconds even for 50+ points.

📖 **For detailed algorithm explanations, see [ALGORITHMS.md](ALGORITHMS.md)**

## Development

### Docker Development Workflow

```bash
# Start services in detached mode
make up

# Watch logs
make logs-api

# Make code changes (volume is mounted, so changes reflect immediately after restart)
# Restart API service
make restart-api

# Stop everything
make down
```

### Local Development Workflow

```bash
# Start with hot reload
make dev
# or
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run without hot reload
make run
# or
uv run python main.py
```

### Accessing Services

- **API**: `http://localhost:8000`
- **API Health**: `http://localhost:8000/health`
- **RabbitMQ Management UI**: `http://localhost:15672` (credentials: guest/guest)

## Testing

### Using the Test Script

```bash
# Make sure services are running first
make up

# Send test requests
make test-map       # Send map processing request
make test-tsp       # Send TSP request (after map is processed)
make test-consume   # Listen for responses
make test-full      # Run complete test workflow

# Test TSP algorithms (compare performance)
make test-algorithms  # Compare brute force vs heuristic algorithms
```

### Manual Testing

You can also test using the RabbitMQ Management UI at `http://localhost:15672` (default credentials: guest/guest) or by publishing messages directly to the queues as shown in the usage examples.

## Docker Commands

```bash
# Build images
make build
docker-compose build

# Start services
make up
docker-compose up -d

# View logs
make logs
docker-compose logs -f api
docker-compose logs -f rabbitmq

# Stop services
make down
docker-compose down

# Clean everything (including volumes)
make clean
docker-compose down -v

# Shell access
make shell-api
docker-compose exec api /bin/sh

# Check service status
make ps
docker-compose ps
```

## Environment Variables

You can customize the application by setting environment variables in `docker-compose.yml` or creating a `.env` file:

```env
RABBITMQ_HOST=rabbitmq
MAP_REQUEST_QUEUE=map_processing_requests
MAP_RESPONSE_QUEUE=map_processing_responses
TSP_REQUEST_QUEUE=tsp_requests
TSP_RESPONSE_QUEUE=tsp_responses
```
