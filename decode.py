import numpy as np
import cv2
import io
from PIL import Image
from model import SECRET_SHAPE, IMAGE_SHAPE, image_to_text

def decode_image(stego_image_bytes, decoder_model):
    """
    Decoder -> extracts hidden data
    """
    # Ensure consistent preprocessing (resize, normalize) 
    # Correct image normalization (0-1 during processing)
    image_obj = Image.open(io.BytesIO(stego_image_bytes)).convert('RGB')
    arr = np.array(image_obj)
    arr = cv2.resize(arr, (IMAGE_SHAPE[1], IMAGE_SHAPE[0]))
    stego_norm = arr.astype(np.float32) / 255.0
    stego_batch = np.expand_dims(stego_norm, axis=0)
    
    # Fix decoding logic so hidden data is properly retrieved
    decoded_batch = decoder_model.predict(stego_batch, verbose=0)
    extracted_data_map = decoded_batch[0]
    
    # Convert float map back to string text
    extracted_text = image_to_text(extracted_data_map)
    return extracted_text
