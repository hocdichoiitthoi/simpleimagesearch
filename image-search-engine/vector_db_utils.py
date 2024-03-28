from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import PointStruct
import numpy as np
import os
from tqdm import tqdm

PATH = "D:\\image-search-engine\\local\\data\\feature"
client = QdrantClient(host="localhost", port=6333)
if not client.collection_exists("image-search"):
    client.create_collection("image-search",
                            vectors_config=VectorParams(size=4, distance=Distance.EUCLID))

for index, vector_path in tqdm(enumerate(os.listdir(PATH)), unit="vector", desc="Push vector to database"):
    embedding_vector = np.load(os.path.join(PATH, vector_path))
    client.upsert(collection_name="image-search",
                  wait=True,
                  points=[
                      PointStruct(id=index,
                                  vector=embedding_vector,
                                  payload={"img_path": f"{PATH}/{vector_path}"})])

