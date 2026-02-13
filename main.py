import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rabbitmq_handler import RabbitMQHandler
import threading

# RabbitMQ configuration from environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
MAP_REQUEST_QUEUE = os.getenv("MAP_REQUEST_QUEUE", "map_processing_requests")
MAP_RESPONSE_QUEUE = os.getenv("MAP_RESPONSE_QUEUE", "map_processing_responses")
TSP_REQUEST_QUEUE = os.getenv("TSP_REQUEST_QUEUE", "tsp_requests")
TSP_RESPONSE_QUEUE = os.getenv("TSP_RESPONSE_QUEUE", "tsp_responses")

# Initialize RabbitMQ handler
rabbitmq_handler = RabbitMQHandler(
    host=RABBITMQ_HOST,
    map_request_queue=MAP_REQUEST_QUEUE,
    map_response_queue=MAP_RESPONSE_QUEUE,
    tsp_request_queue=TSP_REQUEST_QUEUE,
    tsp_response_queue=TSP_RESPONSE_QUEUE,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI.
    Manages startup and shutdown events.
    """
    # Startup: Initialize RabbitMQ queues and start consumer
    rabbitmq_handler.setup_queues()

    # Start consumer in a separate thread
    consumer_thread = threading.Thread(
        target=rabbitmq_handler.start_consuming, daemon=True
    )
    consumer_thread.start()

    print("RabbitMQ consumer started")

    yield

    # Shutdown: cleanup code would go here if needed
    print("Application shutting down")


app = FastAPI(title="Map Processing and TSP API", lifespan=lifespan)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Map Processing and TSP API",
        "queues": {
            "map_request": MAP_REQUEST_QUEUE,
            "map_response": MAP_RESPONSE_QUEUE,
            "tsp_request": TSP_REQUEST_QUEUE,
            "tsp_response": TSP_RESPONSE_QUEUE,
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
