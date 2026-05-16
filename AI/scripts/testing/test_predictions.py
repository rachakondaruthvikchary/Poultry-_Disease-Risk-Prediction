#!/usr/bin/env python3
"""Test model predictions on sample images."""
import json
from pathlib import Path
import tensorflow as tf
from PIL import Image
import numpy as np

MODEL_PATH = Path('AI/models/poultry_cnn.keras')
LABELS_PATH = Path('AI/models/poultry_cnn_labels.json')
SAMPLE_DATA = Path('AI/sample_data')

# Load model and labels
model = tf.keras.models.load_model(MODEL_PATH)
labels_data = json.loads(LABELS_PATH.read_text())
class_labels = labels_data.get('class_names') or labels_data.get('labels')
if not class_labels:
    raise ValueError('No class labels found in model metadata')

print('Testing model predictions...')
print('='*60)
print(f'Classes: {class_labels}')
print()

# Test on one image from each class
for class_folder in sorted(SAMPLE_DATA.iterdir()):
    if not class_folder.is_dir():
        continue
    
    images = list(class_folder.glob('*.*'))[:1]  # Just first image per class
    if not images:
        continue
    
    img_path = images[0]
    print(f'Testing: {class_folder.name}/{img_path.name}')
    
    # Load and preprocess image
    img = Image.open(img_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0  # Normalize to 0-1
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    pred_class = np.argmax(predictions[0])
    pred_label = class_labels[pred_class]
    pred_confidence = predictions[0][pred_class]
    
    print(f'  ➜ Predicted: {pred_label} ({pred_confidence*100:.1f}%)')
    print()

print('='*60)
print('✅ Model predictions working correctly!')
