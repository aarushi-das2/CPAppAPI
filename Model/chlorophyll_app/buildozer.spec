[app]
title = Chlorophyll Predictor
package.name = chlorophyllpredictor
package.domain = org.chlorophyll.predictor
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,pkl
version = 1.0.0
requirements = python3,kivy,opencv-python-headless,numpy,pandas,joblib,plyer
orientation = portrait
fullscreen = 0

# Include trained artifacts in APK
source.include_patterns = chlorophyll_rf_model.pkl,feature_columns.pkl

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = False
android.logcat_filters = *:S python:D
