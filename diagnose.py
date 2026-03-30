import os
import tensorflow as tf
import numpy as np
from model import build_models

print(f"TensorFlow version: {tf.__version__}")

IMAGE_SHAPE = (64, 64, 3)
SECRET_SHAPE = (64, 64, 1)

WEIGHTS_DIR = 'weights'
encoder_path = os.path.join(WEIGHTS_DIR, 'encoder.keras')
decoder_path = os.path.join(WEIGHTS_DIR, 'decoder.keras')

print("\nChecking file existence:")
print(f"Encoder exists: {os.path.exists(encoder_path)}")
print(f"Decoder exists: {os.path.exists(decoder_path)}")

print("\nAttempting to build models from scratch...")
try:
    e, d, f = build_models(IMAGE_SHAPE, SECRET_SHAPE)
    print("✓ Successfully built model architecture")
except Exception as err:
    print(f"✗ Failed to build model architecture: {err}")

print("\nAttempting to load weights:")
if os.path.exists(encoder_path):
    try:
        encoder = tf.keras.models.load_model(encoder_path, compile=False)
        print("✓ Encoder loaded successfully")
        encoder.summary()
    except Exception as err:
        print(f"✗ Encoder load error: {err}")

if os.path.exists(decoder_path):
    try:
        decoder = tf.keras.models.load_model(decoder_path, compile=False)
        print("✓ Decoder loaded successfully")
        decoder.summary()
    except Exception as err:
        print(f"✗ Decoder load error: {err}")

print("\nDone.")
