from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission

import os
from pathlib import Path
from threading import Thread
from time import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from plyer import camera

from predictor import ChlorophyllPredictor


class ChlorophyllApp(App):
    def build(self):
        if platform == "android":
            request_permissions([
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        Window.clearcolor = (0.96, 0.97, 0.99, 1)
        self.predictor = ChlorophyllPredictor()

        self.current_image_path = None
        self.predicting = False

        self.root_layout = BoxLayout(orientation="vertical", padding=20, spacing=16)

        self.title_label = Label(
            text="Chlorophyll Predictor",
            size_hint=(1, 0.12),
            color=(0.08, 0.16, 0.28, 1),
            bold=True,
            font_size="30sp",
        )
        self.root_layout.add_widget(self.title_label)

        self.preview = Image(
            source="",
            size_hint=(1, 0.48),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.root_layout.add_widget(self.preview)

        self.info_label = Label(
            text="Capture a leaf image to begin.",
            size_hint=(1, 0.12),
            color=(0.22, 0.27, 0.35, 1),
            font_size="18sp",
            halign="center",
            valign="middle",
        )
        self.info_label.bind(size=self._sync_info_text)
        self.root_layout.add_widget(self.info_label)

        self.button_area = BoxLayout(orientation="vertical", spacing=12, size_hint=(1, 0.28))
        self.root_layout.add_widget(self.button_area)

        self.render_home()
        return self.root_layout

    def _sync_info_text(self, *_):
        self.info_label.text_size = self.info_label.size

    def clear_buttons(self):
        self.button_area.clear_widgets()

    def create_button(self, text, bg, handler):
        btn = Button(
            text=text,
            size_hint=(1, None),
            height="58dp",
            background_normal="",
            background_color=bg,
            color=(1, 1, 1, 1),
            font_size="18sp",
            bold=True,
        )
        btn.bind(on_release=handler)
        return btn

    def render_home(self):
        self.clear_buttons()
        self.button_area.add_widget(
            self.create_button("Capture Image", (0.16, 0.48, 0.92, 1), self.capture_image)
        )

    def render_preview_actions(self):
        self.clear_buttons()
        self.button_area.add_widget(
            self.create_button("Predict", (0.10, 0.62, 0.36, 1), self.predict_image)
        )
        self.button_area.add_widget(
            self.create_button("Retake", (0.93, 0.42, 0.20, 1), self.capture_image)
        )

    def render_result_actions(self):
        self.clear_buttons()
        self.button_area.add_widget(
            self.create_button("Capture Again", (0.16, 0.48, 0.92, 1), self.capture_image)
        )

    def capture_image(self, *_):
        if self.predicting:
            return
        capture_path = Path(self.user_data_dir) / f"leaf_{int(time())}.jpg"
        try:
            camera.take_picture(filename=str(capture_path), on_complete=self.on_camera_complete)
            self.info_label.text = "Opening camera..."
        except Exception:
            self.info_label.text = "Camera is unavailable on this device."

    def on_camera_complete(self, path):
        if not path:
            self.info_label.text = "Camera failed. Try again."
            self.render_home()
            return

        if not os.path.exists(path):
            self.info_label.text = "Image not saved properly."
            self.render_home()
            return

        try:
            self.preview.source = path
            self.preview.reload()
        except Exception:
            self.info_label.text = "Error loading image."
            self.render_home()
            return

        self.current_image_path = path
        self.info_label.text = "Image captured. Tap Predict."
        self.render_preview_actions()

    def predict_image(self, *_):
        if self.predicting:
            return
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.info_label.text = "Invalid image. Please capture again."
            self.render_home()
            return

        self.predicting = True
        self.info_label.text = "Predicting..."
        self.clear_buttons()
        loading = self.create_button("Predicting...", (0.45, 0.50, 0.58, 1), lambda *_: None)
        loading.disabled = True
        self.button_area.add_widget(loading)
        try:
            Thread(target=self._predict_worker, daemon=True).start()
        except Exception:
            self.info_label.text = "Prediction failed to start."
            self.render_preview_actions()

    def _predict_worker(self):
        try:
            value = self.predictor.predict_from_path(self.current_image_path)
            Clock.schedule_once(lambda *_: self._show_prediction(value), 0)
        except Exception:
            Clock.schedule_once(lambda *_: self._show_prediction_error(), 0)

    def _show_prediction(self, value):
        self.predicting = False
        self.info_label.text = f"Chlorophyll: {value:.2f} mg/g"
        self.render_result_actions()

    def _show_prediction_error(self):
        self.predicting = False
        self.info_label.text = "Prediction failed. Please capture a clear image."
        self.render_preview_actions()


if __name__ == "__main__":
    ChlorophyllApp().run()