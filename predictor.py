from pathlib import Path

import cv2
import joblib
import numpy as np
import pandas as pd


class ChlorophyllPredictor:
    def __init__(self, model_path="chlorophyll_rf_model.pkl", columns_path="feature_columns.pkl"):
        base_dir = Path(__file__).resolve().parent
        self.model = joblib.load(str(base_dir / model_path))
        self.feature_columns = joblib.load(str(base_dir / columns_path))

    def extract_rgb_features(self, img):
        img = img.astype(np.float32)

        R = img[:, :, 0]
        G = img[:, :, 1]
        B = img[:, :, 2]

        eps = 1e-6
        total = R + G + B + eps

        r = R / total
        g = G / total
        b = B / total

        return {
            "r_mean": float(r.mean()),
            "g_mean": float(g.mean()),
            "b_mean": float(b.mean()),

            "G_R": float((G / (R + eps)).mean()),
            "G_B": float((G / (B + eps)).mean()),
            "R_B": float((R / (B + eps)).mean()),

            "ExG": float((2*G - R - B).mean()),
            "NGRDI": float(((G - R) / (G + R + eps)).mean()),
            "VARI": float(((G - R) / (G + R - B + eps)).mean()),

            "Intensity": float(((R + G + B) / 3).mean()),
        }

    def extract_texture_features(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return {
            "Gray_std": float(gray.std()),
            "Edge_var": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        }

    def predict_from_path(self, image_path):
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError("Invalid image file or unreadable image.")

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (224, 224), interpolation=cv2.INTER_LINEAR)

        features = {}
        features.update(self.extract_rgb_features(img_rgb))
        features.update(self.extract_texture_features(img_rgb))

        print("FEATURES:", features)

        data = pd.DataFrame([features])
        try:
            data = data[self.feature_columns]
        except KeyError as exc:
            missing = [col for col in self.feature_columns if col not in data.columns]
            raise ValueError(f"Feature mismatch with training columns: {missing}") from exc

        prediction = float(self.model.predict(data)[0])
        return prediction

    def predict_from_image(self, img_bgr):
        if img_bgr is None:
            raise ValueError("Invalid image.")

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (224, 224))

        features = {}
        features.update(self.extract_rgb_features(img_rgb))
        features.update(self.extract_texture_features(img_rgb))

        print("FEATURES:", features)

        data = pd.DataFrame([features])
        try:
            data = data[self.feature_columns]
        except KeyError as exc:
            missing = [col for col in self.feature_columns if col not in data.columns]
            raise ValueError(f"Feature mismatch with training columns: {missing}") from exc

        prediction = float(self.model.predict(data)[0])
        return prediction