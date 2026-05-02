# Chlorophyll Prediction API

A Flask API for predicting chlorophyll content in leaf images using a trained Random Forest model.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the API:
   ```bash
   python app.py
   ```

The API will start on `http://0.0.0.0:5000`

## Endpoint

### POST /predict

Accepts a multipart/form-data request with an image file.

**Request:**
- `image`: The leaf image file (JPEG, PNG, etc.)

**Response:**
```json
{
  "chlorophyll": 42.5
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

## Usage with Android App

The API is designed to work with the Android app that sends images to `http://10.0.2.2:5000/predict` (when running on emulator).

## Model

The API uses:
- `chlorophyll_rf_model.pkl`: Trained Random Forest Regressor
- `feature_columns.pkl`: Feature column names for prediction

Features extracted from images include RGB ratios, vegetation indices (ExG, NGRDI, VARI), and texture features.