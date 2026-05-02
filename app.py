from flask import Flask, request, jsonify
from predictor import ChlorophyllPredictor
import cv2
import numpy as np
import os

app = Flask(__name__)

# Initialize the predictor
predictor = ChlorophyllPredictor()

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400

    try:
        # Read image bytes
        img_bytes = file.read()
        img_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Invalid image file'}), 400

        # Predict chlorophyll value
        chlorophyll = predictor.predict_from_image(img)
        return jsonify({'chlorophyll': chlorophyll})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)