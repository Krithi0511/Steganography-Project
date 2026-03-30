import os
import cv2
import numpy as np
import tensorflow as tf
from model import build_models

def load_data(image_shape=(64, 64, 3), num_samples=1000):
    """
    Load CIFAR-10 dataset as sample cover images for training.
    """
    print(f"Loading {num_samples} samples from CIFAR-10 dataset...")
    (x_train, _), (_, _) = tf.keras.datasets.cifar10.load_data()
    x_train = x_train[:num_samples]
    
    x_train_resized = []
    for img in x_train:
        img_resized = cv2.resize(img, (image_shape[1], image_shape[0]))
        x_train_resized.append(img_resized)
        
    x_train_resized = np.array(x_train_resized, dtype=np.float32) / 255.0
    return x_train_resized

def train():
    image_shape = (64, 64, 3)
    secret_shape = (64, 64, 1)
    
    print("Building models...")
    encoder, decoder, full_model = build_models(image_shape, secret_shape)
    
    full_model.compile(
        optimizer='adam', 
        loss=['mse', 'binary_crossentropy'], 
        loss_weights=[1.0, 5.0]
    )
    
    # full_model.summary()
    
    data_samples = 2000
    covers = load_data(image_shape, num_samples=data_samples)
    
    print("Generating binary secret payloads...")
    secrets = np.random.randint(0, 2, size=(len(covers),) + secret_shape).astype(np.float32)
    
    print("Starting training...")
    full_model.fit(
        [covers, secrets], [covers, secrets], 
        epochs=5,
        batch_size=32, 
        validation_split=0.1
    )
    
    print("\nTraining complete.")
    
    weights_dir = 'weights'
    os.makedirs(weights_dir, exist_ok=True)
    
    encoder.save(os.path.join(weights_dir, 'encoder.keras'))
    decoder.save(os.path.join(weights_dir, 'decoder.keras'))
    print(f"Saved: weights/encoder.keras  &  weights/decoder.keras")

if __name__ == "__main__":
    train()