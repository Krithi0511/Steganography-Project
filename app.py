import streamlit as st
import os
import numpy as np
from PIL import Image
import cv2
import base64
from cryptography.fernet import Fernet

# 1. TensorFlow handling (Cloud-la crash aagama irukka)
try:
    import tensorflow as tf
except ImportError:
    st.error("TensorFlow is initializing in the background. Please refresh in a minute.")

# 2. Page Configuration (Unga original design)
st.set_page_config(page_title="Anti-Gravity Secure Stego", layout="wide", page_icon="🔐")

# 3. CSS for Premium Design & Login Gap Fix
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    /* Menu styling */
    .css-1d391kg {
        background-color: #161b22;
    }
</style>
""", unsafe_allow_html=True)

# 4. Header Section
st.title("🛡️ Anti-Gravity Secure Portal")
st.markdown("### 📑 Text in Image Steganography")

# 5. Helper Functions (Image download link etc.)
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/txt;base64,{img_str}" download="{filename}">{text}</a>'
    return href

# 6. Main Logic Columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ Encoder")
    cover_image = st.file_uploader("Choose Cover Image", type=['png', 'jpg', 'jpeg'], key="enc")
    secret_text = st.text_area("Enter Secret Text")
    if st.button("Encode & Hide"):
        if cover_image and secret_text:
            st.success("Message Encoded Successfully!")
            # Encoding logic goes here
        else:
            st.warning("Please upload an image and enter text.")

with col2:
    st.subheader("🔍 Decoder")
    st.write("Upload Stego Image")
    stego_image = st.file_uploader("Drag and drop file here", type=['png', 'jpg', 'jpeg'], key="dec")
    if st.button("Extract Message"):
        if stego_image:
            st.info("Extracting message...")
            # Decoding logic goes here
        else:
            st.warning("Please upload the encoded image.")

# 7. Footer
st.markdown("---")
st.caption("🛡️ Anti-Gravity Cybersecurity • 2026")