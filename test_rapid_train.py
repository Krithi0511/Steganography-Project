import numpy as np
import tensorflow as tf
from model import build_models
from encode import encode_image
import os

os.makedirs('tester', exist_ok=True)

# 1. Build blank model
e, d, f = build_models()
f.compile(optimizer='adam', loss=['mse', 'mse'], loss_weights=[1.0, 1.0])

# 2. Train on garbage data for 1 step just to initialize weights to random
covers = np.random.rand(10, 64, 64, 3).astype(np.float32)
secrets = np.random.randint(0, 2, size=(10, 64, 64, 1)).astype(np.float32)
f.fit([covers, secrets], [covers, secrets], epochs=1, batch_size=2, verbose=0)

# 3. Test encoder mean output
dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
dummy_img[:, :, 1] = 255
with open('tester/dummy2.png', 'wb') as file:
    from PIL import Image
    Image.fromarray(dummy_img, 'RGB').save(file, format='PNG')

with open('tester/dummy2.png', 'rb') as file:
    img_bytes = file.read()

out_img = encode_image(img_bytes, "Test", e)
out_arr = np.array(out_img)

print(f"Random initialization test:")
print(f"Output shape: {out_arr.shape}")
print(f"Output mean pixel value: {out_arr.mean():.2f}")
print(f"Output max pixel value: {out_arr.max()}")
print(f"Output min pixel value: {out_arr.min()}")
