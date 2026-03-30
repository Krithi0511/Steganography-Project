import numpy as np
import cv2
import io
from PIL import Image
from model import SECRET_SHAPE, IMAGE_SHAPE, text_to_image

def encode_image(cover_image_bytes, secret_data, encoder_model):
    """
    Encoder -> embeds secret data into image
    """
    # Create secret input
    secret_img = text_to_image(secret_data, SECRET_SHAPE)
    secret_batch = np.expand_dims(secret_img, axis=0)
    
    # Preprocessing (resize, normalize)
    # Correct image normalization (use 0-1 during processing)
    image_obj = Image.open(io.BytesIO(cover_image_bytes)).convert('RGB')
    arr = np.array(image_obj)
    arr = cv2.resize(arr, (IMAGE_SHAPE[1], IMAGE_SHAPE[0]))
    cover_norm = arr.astype(np.float32) / 255.0
    cover_batch = np.expand_dims(cover_norm, axis=0)
    
    # Generate Stego Image tensor
    stego_batch = encoder_model.predict([cover_batch, secret_batch], verbose=0)
    
    # Postprocessing (denormalize, convert to displayable image)
    image = stego_batch[0] # The exact variable name for the prompt
    
    # Convert output image to uint8 using EXACT prompt snippet
    stego_uint8 = np.clip(image * 255, 0, 255).astype('uint8')
    
    # Preserve RGB channels properly
    stego_pil = Image.fromarray(stego_uint8, 'RGB')
    return stego_pil
