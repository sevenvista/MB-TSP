"""
Example test script to demonstrate sending requests to the RabbitMQ queues
"""
import pika
import json
import time


def send_map_processing_request():
    """Send a sample map processing request"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Create a sample 5x5 grid map
    # Note: IDs are optional for PATH and OBSTACLE cells (will be auto-generated)
    # IDs are required for START, END, and SHELF cells (needed for TSP routing)
    request = {
        "map": [
            [
                {"type": "START", "id": "start1"},
                {"type": "PATH", "id": null},  # Can use null for auto-generation
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "SHELF", "id": "shelf1"}
            ],
            [
                {"type": "PATH", "id": null},
                {"type": "OBSTACLE", "id": null},
                {"type": "PATH", "id": null},
                {"type": "OBSTACLE", "id": null},
                {"type": "PATH", "id": null}
            ],
            [
                {"type": "SHELF", "id": "shelf2"},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "SHELF", "id": "shelf3"}
            ],
            [
                {"type": "PATH", "id": null},
                {"type": "OBSTACLE", "id": null},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null}
            ],
            [
                {"type": "SHELF", "id": "shelf4"},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "PATH", "id": null},
                {"type": "END", "id": "end1"}
            ]
        ],
        "mapid": "test_warehouse_1"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='map_processing_requests',
        body=json.dumps(request)
    )
    
    print("Map processing request sent!")
    connection.close()


def send_tsp_request():
    """Send a sample TSP request"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    request = {
        "jobid": "test_job_001",
        "mapid": "test_warehouse_1",
        "point_of_interest": ["shelf1", "shelf2", "shelf3", "shelf4"]
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='tsp_requests',
        body=json.dumps(request)
    )
    
    print("TSP request sent!")
    connection.close()


def consume_responses():
    """Consume and print responses from both queues"""
    def map_callback(ch, method, properties, body):
        print(f"\n=== Map Processing Response ===")
        print(json.dumps(json.loads(body), indent=2))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def tsp_callback(ch, method, properties, body):
        print(f"\n=== TSP Response ===")
        print(json.dumps(json.loads(body), indent=2))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.basic_consume(
        queue='map_processing_responses',
        on_message_callback=map_callback
    )
    
    channel.basic_consume(
        queue='tsp_responses',
        on_message_callback=tsp_callback
    )
    
    print("\nWaiting for responses... (Press Ctrl+C to exit)")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_example.py map      # Send map processing request")
        print("  python test_example.py tsp      # Send TSP request")
        print("  python test_example.py consume  # Consume responses")
        print("  python test_example.py full     # Send both requests and consume")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "map":
        send_map_processing_request()
    elif command == "tsp":
        send_tsp_request()
    elif command == "consume":
        consume_responses()
    elif command == "full":
        print("Sending map processing request...")
        send_map_processing_request()
        print("Waiting 2 seconds for processing...")
        time.sleep(2)
        print("Sending TSP request...")
        send_tsp_request()
        print("Consuming responses...")
        time.sleep(1)
        consume_responses()
    else:
        print(f"Unknown command: {command}")
