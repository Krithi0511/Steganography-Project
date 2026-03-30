"""
test_api.py — End-to-end steganography demo
-------------------------------------------
1. Creates a vivid test image in test_images/
2. POSTs to /encode  → saves stego_image.png in output/
3. POSTs to /decode  → prints recovered text

Run:  python test_api.py
(Flask API must be running in a separate terminal: python app.py)
"""

import os
import sys
import time
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────────
API_BASE         = "http://127.0.0.1:5000"
TEST_IMAGE_PATH  = os.path.join("test_images", "cover.png")
STEGO_IMAGE_PATH = os.path.join("output", "stego_image.png")
SECRET_TEXT      = "Hello! This is a secret message hidden with CNN steganography."

os.makedirs("test_images", exist_ok=True)
os.makedirs("output",      exist_ok=True)


def create_test_image():
    """Generate a vivid 256×256 gradient test image."""
    width, height = 256, 256
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(255 * (1 - x / width))
            pixels[x, y] = (r, g, b)

    # Overlay a simple label
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, 252, 30], fill=(0, 0, 0, 160))
    draw.text((8, 8), "Cover Image — Steganography Demo", fill=(255, 255, 255))

    img.save(TEST_IMAGE_PATH)
    print(f"[✓] Test image saved → {TEST_IMAGE_PATH}")


def wait_for_api(timeout=30):
    """Wait until the Flask server is responding."""
    print(f"Connecting to API at {API_BASE} …", end="", flush=True)
    for _ in range(timeout):
        try:
            r = requests.get(API_BASE, timeout=2)
            if r.status_code == 200:
                print(" ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print(".", end="", flush=True)
        time.sleep(1)
    print("\n[✗] Cannot reach API. Make sure `python app.py` is running.")
    return False


def encode(image_path, text):
    print(f"\n[→] Encoding text into image …")
    print(f"    Text : \"{text}\"")
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/encode",
            files={"image": ("cover.png", f, "image/png")},
            data={"text": text},
            timeout=60,
        )
    if response.status_code == 200:
        with open(STEGO_IMAGE_PATH, "wb") as out:
            out.write(response.content)
        print(f"[✓] Stego image saved → {STEGO_IMAGE_PATH}")
    else:
        print(f"[✗] Encode failed: {response.json()}")
        sys.exit(1)


def decode(stego_path):
    print(f"\n[→] Decoding hidden text from stego image …")
    with open(stego_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/decode",
            files={"image": ("stego_image.png", f, "image/png")},
            timeout=60,
        )
    if response.status_code == 200:
        result = response.json()
        print(f"[✓] Decoded text : \"{result.get('extracted_text', '')}\"")
    else:
        print(f"[✗] Decode failed: {response.json()}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("  Steganography End-to-End Test")
    print("=" * 60)

    # 1. Create test image
    create_test_image()

    # 2. Wait for API
    if not wait_for_api():
        sys.exit(1)

    # 3. Encode
    encode(TEST_IMAGE_PATH, SECRET_TEXT)

    # 4. Decode
    decode(STEGO_IMAGE_PATH)

    print("\n" + "=" * 60)
    print("  Done! Check output/stego_image.png")
    print("=" * 60)
