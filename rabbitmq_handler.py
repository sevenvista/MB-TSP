import pika
import json
import uuid
import traceback
from typing import Callable
from models import (
    MapProcessRequest, 
    MapProcessResponse, 
    TSPRequest, 
    TSPResponse
)
from map_processor import MapProcessor
from tsp_solver import solve_tsp


class RabbitMQHandler:
    def __init__(
        self, 
        host: str = 'localhost',
        map_request_queue: str = 'map_processing_requests',
        map_response_queue: str = 'map_processing_responses',
        tsp_request_queue: str = 'tsp_requests',
        tsp_response_queue: str = 'tsp_responses',
        max_retries: int = 5,
        retry_delay: int = 5
    ):
        self.host = host
        self.map_request_queue = map_request_queue
        self.map_response_queue = map_response_queue
        self.tsp_request_queue = tsp_request_queue
        self.tsp_response_queue = tsp_response_queue
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.map_processor = MapProcessor()
        
    def get_connection(self):
        """Create a new RabbitMQ connection with retry logic"""
        import time
        
        for attempt in range(self.max_retries):
            try:
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    connection_attempts=3,
                    retry_delay=2
                )
                connection = pika.BlockingConnection(parameters)
                print(f"Successfully connected to RabbitMQ at {self.host}")
                return connection
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Failed to connect to RabbitMQ after {self.max_retries} attempts")
                    raise
    
    def setup_queues(self):
        """Setup all required queues"""
        connection = self.get_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue=self.map_request_queue, durable=True)
        channel.queue_declare(queue=self.map_response_queue, durable=True)
        channel.queue_declare(queue=self.tsp_request_queue, durable=True)
        channel.queue_declare(queue=self.tsp_response_queue, durable=True)
        
        connection.close()
    
    def publish_message(self, queue: str, message: dict):
        """Publish a message to a queue"""
        connection = self.get_connection()
        channel = connection.channel()
        
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        connection.close()
    
    def handle_map_processing(self, ch, method, properties, body):
        """Handle map processing requests"""
        jobid = str(uuid.uuid4())
        
        try:
            # Parse request
            data = json.loads(body)
            request = MapProcessRequest(**data)
            
            # Process the map
            self.map_processor.process_map(request.map, request.mapid)
            
            # Send success response
            response = MapProcessResponse(
                jobid=jobid,
                status="complete"
            )
            
            self.publish_message(
                self.map_response_queue, 
                response.model_dump()
            )
            
            print(f"Map processing completed for mapid: {request.mapid}, jobid: {jobid}")
            
        except Exception as e:
            # Send error response
            error_msg = f"Error processing map: {str(e)}\n{traceback.format_exc()}"
            response = MapProcessResponse(
                jobid=jobid,
                status="error",
                errormessage=error_msg
            )
            
            self.publish_message(
                self.map_response_queue, 
                response.model_dump()
            )
            
            print(f"Error in map processing: {error_msg}")
        
        finally:
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def handle_tsp(self, ch, method, properties, body):
        """Handle TSP requests"""
        try:
            # Parse request
            data = json.loads(body)
            request = TSPRequest(**data)
            
            # Load distance data
            distances = self.map_processor.load_distances(request.mapid)
            
            # Solve TSP
            optimal_path = solve_tsp(distances, request.point_of_interest)
            
            if optimal_path is None:
                response = TSPResponse(
                    jobid=request.jobid,
                    status="error",
                    errormessage="No valid path found for the given points"
                )
            else:
                response = TSPResponse(
                    point_of_interest=optimal_path,
                    jobid=request.jobid,
                    status="complete"
                )
            
            self.publish_message(
                self.tsp_response_queue, 
                response.model_dump()
            )
            
            print(f"TSP processing completed for jobid: {request.jobid}")
            
        except FileNotFoundError as e:
            response = TSPResponse(
                jobid=request.jobid,
                status="error",
                errormessage=str(e)
            )
            
            self.publish_message(
                self.tsp_response_queue, 
                response.model_dump()
            )
            
            print(f"Error in TSP processing: {str(e)}")
            
        except Exception as e:
            error_msg = f"Error processing TSP: {str(e)}\n{traceback.format_exc()}"
            response = TSPResponse(
                jobid=request.jobid,
                status="error",
                errormessage=error_msg
            )
            
            self.publish_message(
                self.tsp_response_queue, 
                response.model_dump()
            )
            
            print(f"Error in TSP processing: {error_msg}")
        
        finally:
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def start_consuming(self):
        """Start consuming messages from both queues"""
        connection = self.get_connection()
        channel = connection.channel()
        
        # Setup queues
        channel.queue_declare(queue=self.map_request_queue, durable=True)
        channel.queue_declare(queue=self.tsp_request_queue, durable=True)
        
        # Set prefetch count to 1 for fair dispatch
        channel.basic_qos(prefetch_count=1)
        
        # Setup consumers
        channel.basic_consume(
            queue=self.map_request_queue,
            on_message_callback=self.handle_map_processing
        )
        
        channel.basic_consume(
            queue=self.tsp_request_queue,
            on_message_callback=self.handle_tsp
        )
        
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
