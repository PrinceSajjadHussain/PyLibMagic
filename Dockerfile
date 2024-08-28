# Base image for FastAPI
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 7000

# Command to run the FastAPI application
CMD ["uvicorn", "load_balancer:app", "--host", "0.0.0.0", "--port", "7000", "--reload"]
