from flask import Flask, request, jsonify
from predictor import ChlorophyllPredictor
import os
import tempfile

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

    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Predict chlorophyll value
        chlorophyll = predictor.predict_from_path(temp_path)
        return jsonify({'chlorophyll': chlorophyll})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)