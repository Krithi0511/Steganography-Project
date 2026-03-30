import tensorflow as tf
import numpy as np
from encode import encode_image
from PIL import Image
import os

encoder = tf.keras.models.load_model('weights/encoder.keras', compile=False)

# Make a small dummy green block image
dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
dummy_img[:, :, 1] = 255
dummy_pil = Image.fromarray(dummy_img, 'RGB')
os.makedirs('tester', exist_ok=True)
dummy_pil.save('tester/dummy.png')

with open('tester/dummy.png', 'rb') as f:
    img_bytes = f.read()

secret = "Test"
print("Encoding...")
from encode import encode_image
from model import SECRET_SHAPE, IMAGE_SHAPE, text_to_image
import cv2
import io

# Test raw predictions directly
secret_img = text_to_image(secret, SECRET_SHAPE)
secret_batch = np.expand_dims(secret_img, axis=0)

image_obj = Image.open(io.BytesIO(img_bytes)).convert('RGB')
arr = np.array(image_obj)
arr = cv2.resize(arr, (IMAGE_SHAPE[1], IMAGE_SHAPE[0]))
cover_norm = arr.astype(np.float32) / 255.0
cover_batch = np.expand_dims(cover_norm, axis=0)

stego_batch = encoder.predict([cover_batch, secret_batch], verbose=0)
raw_out = stego_batch[0]

with open("tester/output.txt", "w") as out:
    out.write(f"Raw shape: {raw_out.shape}\n")
    out.write(f"Raw dtype: {raw_out.dtype}\n")
    out.write(f"Raw Mean: {raw_out.mean():.6f}\n")
    out.write(f"Raw Max: {raw_out.max():.6f}\n")
    out.write(f"Raw Min: {raw_out.min():.6f}\n")


# out_img.save('tester/out.png')
print("Done saving tester/out.png")
