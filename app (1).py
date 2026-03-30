import streamlit as st
from text_stego import TextSteganography
from utils import get_image_download_link
from PIL import Image
import os
import io
import numpy as np
import base64

# SETTINGS
st.set_page_config(page_title="Secure Stego", layout="wide", page_icon="🛡️")

# CSS for Premium Design & Login Gap Fix
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
    
    * { font-family: 'Outfit', sans-serif; }
    
    [data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
    section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }
    h1 { font-size: 2rem !important; margin-bottom: 0.5rem !important; }
    
    .navbar {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .nav-title { color: white; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
    
    .footer {
        text-align: center; padding: 1rem; color: #94a3b8; border-top: 1px solid #e2e8f0; margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)



# NAVBAR
st.markdown(f"""
<div class="navbar">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div class="nav-title">🛡️ Secure Stego</div>
        <div style="color: white; font-weight: 500;">
            👤 User
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR MODES
mode = st.sidebar.selectbox("🚀 Select Steganography Mode", 
                           ["📝 Text in Image (CNN)", 
                            "📄 Image in Text (Unicode)", 
                            "🔏 Text in Text (Unicode)"])

if mode == "📝 Text in Image (CNN)":
    st.header("📝 Text in Image Steganography")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ Encoder")
        cover_file = st.file_uploader("Choose Cover Image", type=['png','jpg','jpeg'], key="c_tii")
        secret_text = st.text_area("Enter Secret Text", height=100, max_chars=500, key="s_tii")
        
        if cover_file and secret_text:
            cover_img = Image.open(cover_file)
            
            def encode_text_lsb(image, text):
                data = text.encode('utf-8')
                img_arr = np.array(image.convert("RGB"))
                binary_data = ''.join([format(b, '08b') for b in data]) + '1111111111111110'
                flat = img_arr.flatten()
                new_flat = flat.copy()
                data_idx = 0
                for i in range(len(flat)):
                    if data_idx < len(binary_data):
                        # Use 254 instead of ~1 to avoid signed/unsigned overflow issues
                        new_flat[i] = (int(flat[i]) & 254) | int(binary_data[data_idx])
                        data_idx += 1
                    else: break
                return Image.fromarray(new_flat.reshape(img_arr.shape).astype(np.uint8))

            if st.button("🛡️ Hide Text in Image", type="primary"):
                stego_img = encode_text_lsb(cover_img, secret_text)
                st.session_state["last_stego_text"] = stego_img
                st.image(stego_img, caption="Encoded Image", width="stretch")
                
                # Calculate PSNR
                import math
                arr1 = np.array(cover_img.convert("RGB")).astype(np.float64)
                arr2 = np.array(stego_img.convert("RGB")).astype(np.float64)
                mse = np.mean((arr1 - arr2) ** 2)
                if mse == 0:
                    psnr_val = float('inf')
                    psnr_str = "∞ dB"
                else:
                    psnr_val = 20 * math.log10(255.0 / math.sqrt(mse))
                    psnr_str = f"{psnr_val:.2f} dB"
                    
                st.metric("Image Quality (PSNR)", psnr_str, help="Higher is better. >30dB is considered good.")

                buf = io.BytesIO()
                stego_img.save(buf, format='PNG')
                st.download_button("💾 Download Stego Image", buf.getvalue(), "stego_text.png")

    with col2:
        st.subheader("🔍 Decoder")
        stego_file = st.file_uploader("Upload Stego Image", type=['png','jpg','jpeg'], key="stg_tii")
        if stego_file:
            stg_img = Image.open(stego_file)
            if st.button("🔓 Extract Secret Text", type="primary"):
                def decode_text_lsb(encoded_image):
                    bin_data = []
                    img_arr = np.array(encoded_image.convert("RGB"))
                    flat = img_arr.flatten()
                    for val in flat:
                        bin_data.append(str(val % 2))
                        if len(bin_data) >= 16 and "".join(bin_data[-16:]) == '1111111111111110':
                            break
                    
                    bin_str = "".join(bin_data)
                    data_bytes = [int(bin_str[i:i+8], 2) for i in range(0, len(bin_str)-16, 8)]
                    return bytes(data_bytes).decode('utf-8', errors='ignore')
                extracted = decode_text_lsb(stg_img)
                st.success(f"**Extracted Message:** {extracted}")

elif mode == "📄 Image in Text (Unicode)":
    st.header("📄 Image in Text (Invisible Unicode)")
    text_stego = TextSteganography()
    sub_mode = st.radio("Task:", ["🔒 Hide Image", "🔓 Reveal Image"], horizontal=True)
    
    if sub_mode == "🔒 Hide Image":
        cover_text = st.text_area("📄 Cover Text", placeholder="Paste normal text here...", height=150)
        secret_img_file = st.file_uploader("Upload Secret Image", type=["png", "jpg", "jpeg"])
        if st.button("🔥 Inject Image into Text"):
            if cover_text and secret_img_file:
                with st.spinner("Encoding image into text..."):
                    # Resize image if too large to keep stego text manageable
                    img = Image.open(secret_img_file)
                    if img.width > 200 or img.height > 200:
                        img.thumbnail((200, 200))
                    
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    img_bytes = buf.getvalue()
                    
                    b64_img = base64.b64encode(img_bytes).decode('utf-8')
                    stego_text = text_stego.hide_text(cover_text, f"IMG:{b64_img}")
                    
                    st.subheader("Resulting Stego Text")
                    if len(stego_text) < 5000:
                        st.code(stego_text, language=None)
                    else:
                        st.info(f"Stego text generated ({len(stego_text)} chars). Use the download button below.")
                    
                    st.download_button("📥 Download Stego Text (.txt)", 
                                     stego_text, 
                                     file_name="stego_doc.txt",
                                     mime="text/plain")

    else:
        stego_file = st.file_uploader("📂 Upload Stego Document (.txt)", type=["txt"], key="stg_it")
        if st.button("🕵️ Reveal Hidden Image") and stego_file:
            with st.spinner("Searching for hidden image..."):
                # Read the content of the uploaded text file
                reveal_input = stego_file.read().decode("utf-8")
                extracted = text_stego.reveal_text(reveal_input, max_length=500000)
                if extracted.startswith("IMG:"):
                    try:
                        b64_data = extracted[4:]
                        img_data = base64.b64decode(b64_data)
                        st.image(io.BytesIO(img_data), caption="Extracted Secret Image")
                    except Exception as e: 
                        st.error(f"Failed to decode image data: {str(e)}")
                else: 
                    st.warning("No hidden image found or text was corrupted.")
        elif not stego_file:
            st.info("Please upload a .txt file containing the hidden image.")

elif mode == "🔏 Text in Text (Unicode)":
    st.header("🔏 Text in Text (Invisible Unicode)")
    text_stego = TextSteganography()
    sub_mode = st.radio("Task:", ["🔒 Hide Message", "🔓 Reveal Message"], horizontal=True, key="tit_mode")
    if sub_mode == "🔒 Hide Message":
        cover_text = st.text_area("📄 Cover Document", height=150)
        secret_msg = st.text_area("🔐 Secret Message", height=100)
        if st.button("🔥 Inject Secret"):
            if cover_text and secret_msg:
                stego_text = text_stego.hide_text(cover_text, secret_msg)
                st.code(stego_text)
    else:
        reveal_input = st.text_area("📋 Paste Stego Text", height=250, key="tit_reveal")
        if st.button("🕵️ Reveal Hidden Secret"):
            extracted = text_stego.reveal_text(reveal_input)
            st.success(f"**Found Secret:** {extracted}")

# FOOTER
st.markdown("""<div class="footer">🛡️ Anti-Gravity Cybersecurity • 2026</div>""", unsafe_allow_html=True)
