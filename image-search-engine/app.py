from fastapi import FastAPI, UploadFile, File
import os
from PIL import Image
from torchvision import transforms
import tritonclient.http as httpclient
from qdrant_client import QdrantClient
app = FastAPI()

triton_host = os.getenv("TRITON_HOST") or "triton"
qdrant_host = os.getenv("QDRANT_HOST") or "qdrant"
triton_http_endpoint = triton_host + ":8000"
triton_grpc_endpoint = triton_host + ":8001"

triton_client = httpclient.InferenceServerClient(url=triton_http_endpoint)
qdrant_client = QdrantClient(qdrant_host, port=os.getenv("QDRANT_PORT") or 6333)
def vgg16_preprocess(img_path):
    img = Image.open(img_path)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return preprocess(img).numpy()

def triton_infer(buffer):
    transformed_img = vgg16_preprocess(buffer)
    inputs = httpclient.InferInput("input__0", transformed_img.shape, datatype="FP32")
    inputs.set_data_from_numpy(transformed_img, binary_data=True)
    outputs = httpclient.InferRequestedOutput("output__0", binary_data=True)
    results = triton_client.infer(model_name="vgg16", inputs=[inputs], outputs=[outputs])
    return results.as_numpy("output__0")

@app.route('/vector/compare/')
async def compare(f: UploadFile = File(...)):
    with open(f.filename, "wb") as buffer:
        output_vector = triton_infer(buffer)
        result = qdrant_client.search(output_vector)
        result = [vector.payload for vector in result]
    return {'payload': result}
