<<<<<<< HEAD
# Base image
FROM python:3.9-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
# EXPOSE 8000

# Set working directory
WORKDIR /app

# Entrypoint command
CMD ["uvicorn", "server:nt","--reload"]
=======
FROM python:3.9-slim

# Set the working directory 
WORKDIR /usr/src/app

# Install  packages
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy the current directory contents 
COPY . .

# Install packages in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 
EXPOSE 8000

# Define environment variable
ENV NAME ImageSearchEngine

# Run server.py
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]



>>>>>>> 763acd3a72307665d43df193e875330143228e43
