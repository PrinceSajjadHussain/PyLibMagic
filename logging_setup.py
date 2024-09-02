import logging
from datetime import datetime
from elasticsearch import Elasticsearch
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
    
    # Remove all existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Log format
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
                # Ensure the log entry is structured and includes extra fields
                log_entry = {
                    "@timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage()
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
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_seconds = time.perf_counter()  # Use perf_counter for high-resolution timing
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            # Log exception if needed
            logger.error(f"Exception in {func.__name__}: {e}")
            raise  # Re-raise the exception to maintain original behavior
        finally:
            end_seconds = time.perf_counter()
            execution_time = end_seconds - start_seconds
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Format the log entry as a string
            log_entry = (
                f'functionName: {func.__name__}, '
                f'startTime: {start_time}, '
                f'endTime: {end_time}, '
                f'executionTime: {execution_time:.6f} seconds'
            )
            # Log formatted string
            logger.info(log_entry)
        return result
    return wrapper

