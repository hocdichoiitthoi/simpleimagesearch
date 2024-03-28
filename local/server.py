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


# Initialize FastAPI app
app = FastAPI()

# setup db
client = MongoClient('mongodb://localhost:27017/')
db = client['image_database']
collection = db['image_paths']


#qdrant
QDRANT_URL = "https://da067927-34a2-4b7c-a99a-78bb3fc7006c.us-east4-0.gcp.cloud.qdrant.io:6333"
API_KEY = "cZRxa1Uf63SkRDwlCltjn3_emzjQ2DXi7PRq_eTiuF7S-_v92I8qBA"
COLLECTION_NAME = "image_vectors"
FOLDER_PATH = 'C:\\Users\\Phan Cong Duy\\My Code\\GIt_Repo\\Ex_SIS\\image-search-engine\\local\\data\\feature'
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=API_KEY)


# Load image features (consider caching for performance)
fe = FeatureExtractor()
features = []
img_paths = []

# #mongo db
results = collection.find()
img_paths = [result['img_path'] for result in results]
img_paths = np.array(img_paths)
# print('path 1 ne`',img_paths[1])
for feature_path in Path("./data/feature").glob("*.npy"):
    features.append(np.load(feature_path))
features = np.array(features)

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
    with open("templates/index.html", "r") as file:
        return file.read()


# Define endpoint for image search
@app.post("/search-image")
async def search_image(query_img: UploadFile = File(...)):
    try:
        # Read query image
        img_contents = await query_img.read()
        img = Image.open(io.BytesIO(img_contents))

        # Run search
        query = fe.extract(img)

        #search by qdrant
        result_vectors = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            search_params=models.SearchParams(hnsw_ef=128, exact=False),
            query_vector=query,
            limit=5
        )

        
        names = []
        scores = []
        ids = []
        for point in result_vectors:
            name = point.payload['name']
            score = point.score
            id = point.id
            ids.append(id)
            names.append(name)
            scores.append(score)
            

        #search img_path by nums~id
        result_img_paths = []
        for id in ids:
            result_img_paths.append(img_paths[id-1])



        results = []
        for i in range(len(result_vectors)):

            results.append({
                "image_path": str(result_img_paths[i]),
                "id": int(ids[i]),
                "score": float(scores[i]),
                "name": str(names[i]),
            })
 
        return {"results": results}
    


    except Exception as e:
        print(f"Error processing image: {e}")
        return {"error": "An error occurred while processing the image."}