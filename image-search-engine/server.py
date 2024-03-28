import os
import numpy as np
from PIL import Image
from feature_extractor import FeatureExtractor  # Assuming you have this feature extractor module
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware  # Add CORS middleware for cross-origin requests
import io

#mount static folder
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
from fastapi.responses import HTMLResponse

#mongodb
import pymongo
from pymongo import MongoClient

#qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models

#import  URL APIkey
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

QDRANT_URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
FOLDER_PATH = os.getenv("FOLDER_PATH")

# Initialize FastAPI app
app = FastAPI()

# setup db
client = MongoClient('mongodb://localhost:27017/')
db = client['image_database']
collection = db['image_paths']


#qdrant
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=API_KEY)


# Load image features (consider caching for performance)
fe = FeatureExtractor()
# features = []
img_paths = []

# #mongo db
results = collection.find()
img_paths = [result['img_path'] for result in results]
img_paths = np.array(img_paths)

# Load features from .npy files
# for feature_path in Path("./data/feature").glob("*.npy"):
#     features.append(np.load(feature_path))
# features = np.array(features)



#mount to static folder
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin, you might want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

#mounting
app.mount("/static", StaticFiles(directory="static"), name="static")  # Adjust the path to match your static files directory
# Mount the directory containing the image files
app.mount("/data/image", StaticFiles(directory="data/image"), name="images")

#index-html
@app.get("/", response_class=HTMLResponse)
async def get_index():
    print("cac")
    try:
        with open("templates/index.html", "r") as file:
            return file.read()
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


# Define endpoint for image search
@app.post("/search-image")
async def search_image(query_img: UploadFile = File(...)):
    try:
        # Read query image
        img_contents = await query_img.read()
        img = Image.open(io.BytesIO(img_contents))

        # Extract features from query image
        query = fe.extract(img)

        # Run search in Qdrant
        result_vectors = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            search_params=models.SearchParams(hnsw_ef=128, exact=False),
            query_vector=query,
            limit=5
        )

        # Extract information from search results
        results = []
        for point in result_vectors:
            img_path = img_paths[point.id - 1]
            results.append({
                "image_path": str(img_path),
                "id": point.id,
                "score": float(point.score),
                "name": point.payload['name'],
            })
            print('result ne`',results[-1])
        return {"results": results}

    except Exception as e:
        return {"error": f"An error occurred while processing the image: {e}"}

