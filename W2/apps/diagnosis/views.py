import os
import numpy as np
from PIL import Image
import tensorflow as tf

from django.conf import settings
from django.shortcuts import render, get_object_or_404

from apps.ecg.models import ECGRecord
from .models import Diagnosis
from utils.permissions import role_required

# ✅ MODEL PATH
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'ecg_model.h5')

# ✅ SAFE LOAD
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Model loaded successfully")
    except Exception as e:
        print("❌ Model load error:", e)
else:
    print("❌ Model file not found")

# ✅ CLASSES
classes = [
    "Abnormal Heartbeat",
    "History of MI",
    "Myocardial Infarction",
    "Normal"
]

def preprocess_image(file_path):
    img = Image.open(file_path).convert('RGB')
    img = img.resize((48, 48))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


@role_required(['doctor'])
def run_diagnosis(request, ecg_id):
    ecg = get_object_or_404(ECGRecord, id=ecg_id)

    if model is None:
        return render(request, 'diagnosis/result.html', {
            'result': "Model not loaded",
            'confidence': 0,
            'class': "Error"
        })

    try:
        img_array = preprocess_image(ecg.file.path)
        prediction = model.predict(img_array)

        predicted_index = int(np.argmax(prediction))
        predicted_label = classes[predicted_index]
        confidence = float(np.max(prediction) * 100)

        final_result = "Normal" if predicted_label == "Normal" else "Arrhythmia Detected"

        Diagnosis.objects.update_or_create(
            ecg=ecg,
            defaults={
                'result': final_result,
                'predicted_class': predicted_label,
                'confidence': confidence
            }
        )

        return render(request, 'diagnosis/result.html', {
            'result': final_result,
            'confidence': round(confidence, 2),
            'class': predicted_label
        })

    except Exception as e:
        return render(request, 'diagnosis/result.html', {
            'result': "Error",
            'confidence': 0,
            'class': str(e)
        })


def view_result(request, ecg_id):
    ecg = get_object_or_404(ECGRecord, id=ecg_id)

    diagnosis = Diagnosis.objects.filter(ecg=ecg).order_by('-created_at').first()

    if not diagnosis:
        return render(request, 'diagnosis/result.html', {
            'result': "No diagnosis",
            'confidence': 0,
            'class': "N/A"
        })

    return render(request, 'diagnosis/result.html', {
        'result': diagnosis.result,
        'confidence': round(diagnosis.confidence, 2),
        'class': diagnosis.predicted_class
    })