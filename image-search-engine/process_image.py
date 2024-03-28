from PIL import Image
from feature_extractor import FeatureExtractor
from pathlib import Path
import numpy as np
import tqdm

fe = FeatureExtractor()

for img_path in tqdm.tqdm(sorted(Path("./local/data/image").glob("*.jpg"))):
    feature = np.squeeze(np.reshape(fe.extract(img=Image.open(img_path)), (4096, -1)), axis=-1)
    feature_path = Path("./local/data/feature") / (img_path.stem + ".npy")  # e.g., ./static/feature/xxx.npy
    np.save(feature_path, feature)