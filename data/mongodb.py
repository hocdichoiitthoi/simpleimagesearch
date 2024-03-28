import pymongo
from pymongo import MongoClient
import os

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['image_database']
collection = db['image_paths']
collection.drop()
collection = db['image_paths']

def save_image_paths_to_mongodb(folder_path,base_directory):
    # Iterate over all files in the folder
    i = 1
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            img_path = os.path.join(folder_path, filename)
            # Insert image path into MongoDB
            img_path = os.path.relpath(img_path, base_directory)
            collection.insert_one({'nums':i,'img_path': img_path})
            i+=1
            print(f"Image path {img_path} saved to MongoDB")
    print('last nums',i)
if __name__ == "__main__":
    folder_path = r"./image-search-engine/data/image"
    base_directory = r"./image-search-engine/data/"

    save_image_paths_to_mongodb(folder_path,base_directory)
