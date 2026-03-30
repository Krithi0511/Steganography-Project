import streamlit as st
from PIL import Image
import os
import io
import numpy as np
import base64
import math

# --- STEP 1: EMBEDDED TEXT STEGANOGRAPHY CLASS ---
# (Removing external import to prevent FileNotFoundError on Cloud)
class TextSteganography:
    def __init__(self):
        # Using invisible unicode characters for text-in-text
        self.char_to_bin = {
            '0': '\u200b', # Zero width space
            '1': '\u200c', # Zero width non-joiner
        }
        self.bin_to_char = {v: k for k, v in self.char_to_bin.items()}

    def hide_text(self, cover_text, secret_text):
        binary_secret = ''.join(format(ord(c), '08b') for c in secret_text)
        encoded_chars = ''.join(self.char_to_bin[b] for b in binary_secret)
        return cover_text + encoded_chars

    def reveal_text(self, stego_text, max_length=500000):
        extracted_bin = ""
        for char in stego_text:
            if char in self.bin_to_char:
                extracted_bin += self.bin_to_char[char]
        
        if not extracted_bin: return ""
        
        # Convert binary back to text
        chars = []
        for i in range(0, len(extracted_bin), 8):
            byte = extracted_bin[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars)

# SETTINGS
st.set_page_config(page_title="Anti-Gravity Secure Stego", layout="wide", page_icon="🛡️")

# CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    [data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
    .navbar {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .nav-title { color: white; font-size: 1.5rem; font-weight: 700; }
    .footer { text-align: center; padding: 1rem; color: #94a3b8; border-top: 1px solid #e2e8f0; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# NAVBAR
st.markdown("""<div class="navbar"><div class="nav-title">🛡️ Anti-Gravity Secure Portal</div></div>""", unsafe_allow_html=True)

# SIDEBAR
mode = st.sidebar.selectbox("🚀 Select Steganography Mode", 
                           ["📝 Text in Image (LSB)", 
                            "📄 Image in Text (Unicode)", 
                            "🔏 Text in Text (Unicode)"])

# --- LOGIC: TEXT IN IMAGE ---
if mode == "📝 Text in Image (LSB)":
    st.header("📝 Text in Image Steganography")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ Encoder")
        cover_file = st.file_uploader("Choose Cover Image", type=['png','jpg','jpeg'])
        secret_text = st.text_area("Enter Secret Text", max_chars=500)
        
        if st.button("🛡️ Hide Text in Image", type="primary") and cover_file and secret_text:
            image = Image.open(cover_file).convert("RGB")
            data = secret_text.encode('utf-8')
            img_arr = np.array(image)
            binary_data = ''.join([format(b, '08b') for b in data]) + '1111111111111110'
            
            flat = img_arr.flatten()
            if len(binary_data) > len(flat):
                st.error("Text too long for this image!")
            else:
                new_flat = flat.copy()
                for i in range(len(binary_data)):
                    new_flat[i] = (int(flat[i]) & 254) | int(binary_data[i])
                
                stego_img = Image.fromarray(new_flat.reshape(img_arr.shape).astype(np.uint8))
                st.image(stego_img, caption="Encoded Image")
                
                # PSNR Calculation
                mse = np.mean((img_arr.astype(float) - np.array(stego_img).astype(float)) ** 2)
                psnr = 100 if mse == 0 else 20 * math.log10(255.0 / math.sqrt(mse))
                st.metric("Image Quality (PSNR)", f"{psnr:.2f} dB")

                buf = io.BytesIO()
                stego_img.save(buf, format='PNG')
                st.download_button("💾 Download Stego Image", buf.getvalue(), "stego.png")

    with col2:
        st.subheader("🔍 Decoder")
        stego_file = st.file_uploader("Upload Stego Image", type=['png','jpg','jpeg'], key="dec")
        if st.button("🔓 Extract Secret Text") and stego_file:
            img = Image.open(stego_file).convert("RGB")
            flat = np.array(img).flatten()
            bin_data = ""
            for val in flat:
                bin_data += str(val % 2)
                if bin_data.endswith('1111111111111110'): break
            
            bytes_data = [int(bin_data[i:i+8], 2) for i in range(0, len(bin_data)-16, 8)]
            st.success(f"**Extracted Message:** {bytes(bytes_data).decode('utf-8', errors='ignore')}")

# --- LOGIC: IMAGE IN TEXT ---
elif mode == "📄 Image in Text (Unicode)":
    st.header("📄 Image in Text")
    ts = TextSteganography()
    sub = st.radio("Task:", ["🔒 Hide Image", "🔓 Reveal Image"], horizontal=True)
    if sub == "🔒 Hide Image":
        c_text = st.text_area("Cover Text")
        s_img = st.file_uploader("Secret Image", type=['png','jpg','jpeg'])
        if st.button("🔥 Inject") and c_text and s_img:
            img = Image.open(s_img)
            img.thumbnail((150, 150)) # Keep it small for text
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode()
            st.code(ts.hide_text(c_text, f"IMG:{b64}"))
    else:
        stego_txt = st.text_area("Paste Stego Text")
        if st.button("🕵️ Reveal") and stego_txt:
            ext = ts.reveal_text(stego_txt)
            if ext.startswith("IMG:"):
                st.image(io.BytesIO(base64.b64decode(ext[4:])))

# --- LOGIC: TEXT IN TEXT ---
elif mode == "🔏 Text in Text (Unicode)":
    st.header("🔏 Text in Text")
    ts = TextSteganography()
    sub = st.radio("Task:", ["🔒 Hide Message", "🔓 Reveal Message"], horizontal=True)
    if sub == "🔒 Hide Message":
        c_txt = st.text_area("Cover Document")
        s_msg = st.text_area("Secret Message")
        if st.button("🔥 Inject") and c_txt and s_msg:
            st.code(ts.hide_text(c_txt, s_msg))
    else:
        reveal_in = st.text_area("Paste Stego Text")
        if st.button("🕵️ Reveal"):
            st.success(f"Found: {ts.reveal_text(reveal_in)}")

st.markdown("""<div class="footer">🛡️ Anti-Gravity Cybersecurity • 2026</div>""", unsafe_allow_html=True)