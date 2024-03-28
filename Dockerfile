# Base image
FROM python:3.10-slim
WORKDIR /app
COPY ./app.py /app
RUN pip install fastapi Pillow uvicorn tritonclient[all] qdrant_client torchvision
COPY . .
<<<<<<< HEAD
EXPOSE 5000
WORKDIR /app
<<<<<<< HEAD
CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "5000", "--reload"]
=======

# Expose port
# EXPOSE 8000

# Set working directory
WORKDIR /app

# Entrypoint command
CMD ["uvicorn", "server:nt","--reload"]
>>>>>>> duyne
=======
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
>>>>>>> Vinnh
