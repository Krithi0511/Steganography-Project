import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, Concatenate
from tensorflow.keras.models import Model
import numpy as np
import cv2
import io
from PIL import Image

IMAGE_SHAPE = (64, 64, 3)
SECRET_SHAPE = (64, 64, 1)
REDUNDANCY = 4

def build_models(image_shape=IMAGE_SHAPE, secret_shape=SECRET_SHAPE):
    """Build the Encoder, Decoder, and combined Steganography Model using a U-Net architecture."""
    # ── ENCODER (U-Net style with Skip Connections) ───────────────────────
    cover_input  = Input(shape=image_shape,  name="cover_input")
    secret_input = Input(shape=secret_shape, name="secret_input")

    # Combine inputs
    x = Concatenate()([cover_input, secret_input])
    
    # Encoder part
    c1 = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    c1 = Conv2D(64, (3, 3), activation='relu', padding='same')(c1)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)
    
    c2 = Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    c2 = Conv2D(128, (3, 3), activation='relu', padding='same')(c2)
    
    # Decoder part (with Skip Connections to preserve high-frequency detail)
    u1 = tf.keras.layers.UpSampling2D((2, 2))(c2)
    u1 = Concatenate()([u1, c1])
    c3 = Conv2D(64, (3, 3), activation='relu', padding='same')(u1)
    c3 = Conv2D(64, (3, 3), activation='relu', padding='same')(c3)
    
    # Residual Output
    residual = Conv2D(image_shape[-1], (3, 3), activation='linear', padding='same')(c3)
    stego_raw = tf.keras.layers.Add()([cover_input, residual])
    stego_output = tf.keras.layers.Activation('sigmoid', name="stego_output")(stego_raw)

    encoder = Model(inputs=[cover_input, secret_input], outputs=stego_output, name="encoder")


    # ── DECODER ─────────────────────────────────────────────────────────────
    stego_input = Input(shape=image_shape, name="stego_input")
    
    d1 = Conv2D(64, (3, 3), activation='relu', padding='same')(stego_input)
    d1 = Conv2D(64, (3, 3), activation='relu', padding='same')(d1)
    dp1 = tf.keras.layers.MaxPooling2D((2, 2))(d1)
    
    d2 = Conv2D(128, (3, 3), activation='relu', padding='same')(dp1)
    d2 = Conv2D(128, (3, 3), activation='relu', padding='same')(d2)
    
    du1 = tf.keras.layers.UpSampling2D((2, 2))(d2)
    du1 = Concatenate()([du1, d1])
    d3 = Conv2D(64, (3, 3), activation='relu', padding='same')(du1)
    d3 = Conv2D(64, (3, 3), activation='relu', padding='same')(d3)
    
    secret_output = Conv2D(secret_shape[-1], (3, 3), activation='sigmoid', padding='same', name="secret_output")(d3)

    decoder = Model(inputs=stego_input, outputs=secret_output, name="decoder")
    
    # ── FULL MODEL ──────────────────────────────────────────────────────────
    generated_stego  = encoder([cover_input, secret_input])
    decoded_secret   = decoder(generated_stego)

    full_model = Model(inputs=[cover_input, secret_input],
                       outputs=[generated_stego, decoded_secret],
                       name="full_stego_model")
    
    return encoder, decoder, full_model


def text_to_image(text, shape=SECRET_SHAPE):
    """Convert a text string to a binary pixel map with redundancy."""
    bits = ''.join(format(ord(c), '08b') for c in text)
    bits += '00000000'          # EOF marker (null byte)

    max_bits = int(np.prod(shape)) // REDUNDANCY
    if len(bits) > max_bits:
        max_chars = (max_bits // 8) - 1
        raise ValueError(f"Text too long! Maximum is {max_chars} characters.")

    bits = bits.ljust(max_bits, '0')
    bit_list = [int(b) for b in bits for _ in range(REDUNDANCY)]
    
    rem = np.prod(shape) - len(bit_list)
    if rem > 0:
        bit_list.extend([0] * rem)
        
    bit_array = np.array(bit_list[:np.prod(shape)], dtype=np.float32)
    return bit_array.reshape(shape)


def image_to_text(image_array):
    """Convert a binary pixel map back to text using redundancy averaging."""
    flat = image_array.flatten()
    chunked = flat[:len(flat) - (len(flat) % REDUNDANCY)].reshape(-1, REDUNDANCY)
    averaged = chunked.mean(axis=1)
    
    bits = np.round(averaged).astype(int)
    chars = []
    
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        val = int(''.join(str(b) for b in byte), 2)
        if val == 0:  # EOF
            break
        if 32 <= val <= 126 or val in (9, 10, 13):
            chars.append(chr(val))
        else:
            chars.append('?')
            
    return ''.join(chars)


# ── CLEAR ENCODE/DECODE PIPELINE ─────────────────────────────────────────────

def encode_image(cover_image_bytes, secret_data, encoder_model):
    """
    Encoder -> embeds secret data into image.
    Maintains image quality, corrects normalization, outputs uint8.
    """
    # 1. Prepare Secret Data
    secret_img = text_to_image(secret_data, SECRET_SHAPE)
    secret_batch = np.expand_dims(secret_img, axis=0) # Shape: (1, 64, 64, 1)

    # 2. Preprocess Cover Image (Resize and Normalize 0-1)
    image_obj = Image.open(io.BytesIO(cover_image_bytes)).convert('RGB')
    arr = np.array(image_obj)
    arr = cv2.resize(arr, (IMAGE_SHAPE[1], IMAGE_SHAPE[0]))
    cover_norm = arr.astype(np.float32) / 255.0  # Normalize to 0-1
    cover_batch = np.expand_dims(cover_norm, axis=0) # Shape: (1, 64, 64, 3)

    # 3. Model Inference
    stego_batch = encoder_model.predict([cover_batch, secret_batch], verbose=0)
    stego_image_norm = stego_batch[0]  # Shape: (64, 64, 3) in [0, 1] range

    # 4. Postprocess (Denormalize -> 0-255 uint8)
    # Fix technical issue: Convert output image to uint8
    stego_uint8 = np.clip(stego_image_norm * 255.0, 0, 255).astype(np.uint8)
    
    # 5. Return displayable image object that preserves RGB
    return Image.fromarray(stego_uint8, 'RGB')


def decode_image(stego_image_bytes, decoder_model):
    """
    Decoder -> extracts hidden data.
    Ensures consistent preprocessing pipeline with encoding.
    """
    # 1. Preprocess Stego Image (Resize and Normalize 0-1)
    image_obj = Image.open(io.BytesIO(stego_image_bytes)).convert('RGB')
    arr = np.array(image_obj)
    arr = cv2.resize(arr, (IMAGE_SHAPE[1], IMAGE_SHAPE[0]))
    stego_norm = arr.astype(np.float32) / 255.0  # Normalize to 0-1
    stego_batch = np.expand_dims(stego_norm, axis=0) # Shape: (1, 64, 64, 3)

    # 2. Model Inference
    decoded_batch = decoder_model.predict(stego_batch, verbose=0)
    extracted_data_map = decoded_batch[0]

    # 3. Retrieve Hidden Data
    extracted_text = image_to_text(extracted_data_map)
    return extracted_text
