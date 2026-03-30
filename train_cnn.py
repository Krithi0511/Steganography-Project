import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dense, Reshape, Concatenate, GlobalAvgPool1D, UpSampling2D
from tensorflow.keras.models import Model

def build_encoder(img_shape=(64, 64, 3), text_shape=(100, 256)):
    img_input = Input(shape=img_shape, name="cover_input")
    text_input = Input(shape=text_shape, name="text_input")
    
    # Simple CNN
    x = Conv2D(32, (3, 3), padding='same', activation='relu')(img_input)
    x = Flatten()(x)
    
    # Merge and generate stego
    merged = Concatenate()([x, Flatten()(text_input)])
    x = Dense(int(np.prod(img_shape)), activation='sigmoid')(merged)
    stego_output = Reshape(img_shape)(x)
    
    encoder = Model(inputs=[img_input, text_input], outputs=stego_output, name="encoder")
    encoder.compile(optimizer='adam', loss='mse')
    return encoder

if __name__ == "__main__":
    print("Building and saving dummy models...")
    encoder = build_encoder()
    decoder = build_encoder() # Simplified for dummy
    encoder.save('encoder.h5')
    decoder.save('decoder.h5')
    print("Success: encoder.h5 and decoder.h5 saved.")
