import tensorflow as tf
from PIL import Image
import numpy as np
import io
import os

# No constants needed for Keras mode

def load_models():
    """Load Keras models from the weights directory."""
    encoder_path = os.path.join('weights', 'encoder.keras')
    decoder_path = os.path.join('weights', 'decoder.keras')
    
    if os.path.exists(encoder_path) and os.path.exists(decoder_path):
        encoder = tf.keras.models.load_model(encoder_path, compile=False)
        decoder = tf.keras.models.load_model(decoder_path, compile=False)
        return encoder, decoder
    else:
        # Return none if weights are missing, app.py should handle this
        return None, None

def process_encode(cover_image, secret_image, encoder):
    """
    Encodes secret into cover image using Keras CNN.
    Improved with LANCZOS interpolation and rounded normalization.
    """
    # 1. Preprocess images (Resize to 64x64 using high-quality LANCZOS)
    c_arr = np.array(cover_image.convert("RGB").resize((64, 64), Image.LANCZOS)).astype(np.float32) / 255.0
    s_arr = np.array(secret_image.convert("L").resize((64, 64), Image.LANCZOS)).astype(np.float32) / 255.0
    
    c_batch = np.expand_dims(c_arr, axis=0)
    s_batch = np.expand_dims(s_arr, axis=0)
    
    # 2. Encode
    stego_batch = encoder.predict([c_batch, s_batch], verbose=0)
    stego_norm = stego_batch[0]
    
    # 3. Postprocess (Use rounding to maintain color fidelity)
    stego_uint8 = np.clip(np.round(stego_norm * 255.0), 0, 255).astype(np.uint8)
    return Image.fromarray(stego_uint8)

def process_decode(stego_image, decoder):
    """
    Extracts secret image from stego image using Keras CNN.
    """
    # 1. Preprocess (Resume to original training size 64x64)
    stg_arr = np.array(stego_image.convert("RGB").resize((64, 64), Image.LANCZOS)).astype(np.float32) / 255.0
    stg_batch = np.expand_dims(stg_arr, axis=0)
    
    # 2. Decode
    decoded_batch = decoder.predict(stg_batch, verbose=0)
    decoded_norm = decoded_batch[0, :, :, 0]
    
    # 3. Postprocess (Round then scale)
    decoded_uint8 = np.clip(np.round(decoded_norm * 255.0), 0, 255).astype(np.uint8)
    return Image.fromarray(decoded_uint8)

def get_image_download_link(img, filename="stego.png"):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
