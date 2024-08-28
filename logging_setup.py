import logging
from datetime import datetime
from elasticsearch import Elasticsearch
import json
import time
import os

# Function to set up logging
def setup_logging(es_hosts='http://localhost:9200', index_name='my_logs'):
    log_folder = 'logs'
    
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    # Configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Generate filename based on current date
    log_file = os.path.join(log_folder, datetime.now().strftime('%Y-%m-%d') + '.log')

    # File Handler to write logs to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    if es_hosts:
        print("Connecting to Elasticsearch")
        # Connect to Elasticsearch
        es = Elasticsearch([es_hosts])
        
        # Define a custom Elasticsearch handler
        class ElasticsearchHandler(logging.Handler):
            def emit(self, record):
                log_entry = {
                    "@timestamp": datetime.utcnow().isoformat(),
                    "message": self.format(record)
                }
                try:
                    es.index(index=index_name, body=log_entry)
                except Exception as e:
                    print("Error while indexing to Elasticsearch:", e)

        # Elasticsearch Handler to log to Elasticsearch
        es_handler = ElasticsearchHandler()
        es_handler.setFormatter(formatter)
        logger.addHandler(es_handler)

    return logger

# Define a global logger variable
logger = setup_logging()

# Function decorator for logging execution details
def log_function_execution(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now().strftime("%I:%M:%S %p")
        start_seconds = time.time()
        try:
            result = func(*args, **kwargs)
        finally:
            end_seconds = time.time()
            execution_time = end_seconds - start_seconds
            end_time = datetime.now().strftime("%I:%M:%S %p")
            logger.info(json.dumps({
                "functionName": func.__name__,
                "startTime": start_time,
                "endTime": end_time,
                "executionTime": execution_time
            }))
        return result
    return wrapper
