import os
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

# load env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

QDRANT_URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("API_KEY")
COLLECTION_NAME = os.getenv("COLLECT_NAME")
FOLDER_PATH = os.getenv("FOLDER_PATH")
# Initialize Qdrant client
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=API_KEY)

# Function to create collection
def create_collection():
    npy_files = [file for file in os.listdir(FOLDER_PATH) if file.endswith('.npy')]
    vector_size = None
    vectors = []
    
    for file_name in npy_files:
        file_path = os.path.join(FOLDER_PATH, file_name)
        vector = np.load(file_path)
        vectors.append(vector)
        vector_size = len(vector)
    
    collections = qdrant_client.list_collections()
    if COLLECTION_NAME in collections:
        print(f"Collection '{COLLECTION_NAME}' exists in Qdrant.")
        return vectors
    else:
        qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    return vectors

# Function to upsert vector
def upsert_vector(vector, index, vector_name):
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=index + 1,
                vector=vector.tolist(),
                payload={
                    "name": vector_name,
                },
            )
        ]
    )

# Main function
def main():
    vectors = create_collection()
    npy_files = [file for file in os.listdir(FOLDER_PATH) if file.endswith('.npy')]
    
    for i, vector in enumerate(vectors):
        upsert_vector(vector, i, npy_files[i])
        print('upsert ne`',i+1)

if __name__ == "__main__":
    main()
