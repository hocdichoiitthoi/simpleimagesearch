from flask import Flask, render_template, request, jsonify, send_from_directory,url_for
from PIL import Image
from io import BytesIO
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'user_imgs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-image', methods=['POST'])
def process_image():
    print('toi day r')
    if request.method == 'POST':
        image_data = request.form.get('data')
        if image_data is None:
            return jsonify({'error': 'Image data is missing'}), 400

        print('Image data received:', image_data)
        
        return jsonify({'processed_image': image_data})
    else:
        return jsonify({'error': 'Method not allowed'}), 405



@app.route('/get-images')
def get_images():
    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    images = []
    for i in range(min(2, len(image_files))):
        images.append(os.path.join(app.config['UPLOAD_FOLDER'], image_files[i]))
    return jsonify({'images': images})

if __name__ == '__main__':
    app.run(debug=True)
