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



# Initialize FastAPI app
app = FastAPI()

# Load image features (consider caching for performance)
fe = FeatureExtractor()
features = []
img_paths = []
for feature_path in Path("./data/feature").glob("*.npy"):
    features.append(np.load(feature_path))
    img_paths.append(Path("./data/image") / (feature_path.stem + ".jpg"))
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
        dists = np.linalg.norm(features - query, axis=1)
        top_results = np.argsort(dists)[:10]  # Top 10 results

        # Format results
        results = []
        for idx in top_results:
            results.append({
                "image_path": str(img_paths[idx]),
                "distance": float(dists[idx])
    })
        return {"results": results}

    except Exception as e:
        print(f"Error processing image: {e}")
        return {"error": "An error occurred while processing the image."}


# Root endpoint

