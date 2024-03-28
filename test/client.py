import tritonclient.http as httpclient
import numpy as np
from PIL import Image
from torchvision import transforms
from tritonclient.utils import triton_to_np_dtype
from pathlib import Path
from pprint import pprint
from qdrant_client import QdrantClient

MAX_QUERY = 10

def vgg16_preprocess(img_path):
    img = Image.open(img_path)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return preprocess(img).numpy()

client = httpclient.InferenceServerClient(url="localhost:8000")
input_image = "D:\\image-search-engine\\server\\xxx.jpg"
transformed_img = vgg16_preprocess(input_image)
inputs = httpclient.InferInput("input__0", transformed_img.shape, datatype="FP32")
inputs.set_data_from_numpy(transformed_img, binary_data=True)
outputs = httpclient.InferRequestedOutput("output__0", binary_data=True)
results = client.infer(model_name="vgg16", inputs=[inputs], outputs=[outputs])
output_vector = results.as_numpy("output__0")

client = QdrantClient(host = "localhost", port=6333)
result = client.search(collection_name="image-search", query_vector=output_vector, limit=MAX_QUERY)
pprint([rs.payload for rs in result])