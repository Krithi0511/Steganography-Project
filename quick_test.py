"""quick_test.py - runs encode then decode against the live Flask API."""
import os
import requests
from PIL import Image, ImageDraw

os.makedirs("test_images", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ── 1. Create a vivid test cover image ──────────────────────────────────────
img = Image.new("RGB", (256, 256))
pix = img.load()
for y in range(256):
    for x in range(256):
        pix[x, y] = (int(255 * x / 256), int(255 * y / 256), int(255 * (1 - x / 256)))
draw = ImageDraw.Draw(img)
draw.rectangle([4, 4, 252, 28], fill=(0, 0, 0))
draw.text((8, 8), "Cover Image - Stego Demo", fill=(255, 255, 255))
img.save("test_images/cover.png")
print("[OK] test_images/cover.png created")

# ── 2. Encode ────────────────────────────────────────────────────────────────
SECRET = "Hello! This is hidden with CNN Steganography."
print("[ENCODE] Secret text:", SECRET)

with open("test_images/cover.png", "rb") as f:
    resp = requests.post(
        "http://127.0.0.1:5000/encode",
        files={"image": ("cover.png", f, "image/png")},
        data={"text": SECRET},
        timeout=60,
    )

print("  HTTP Status:", resp.status_code)
if resp.status_code == 200:
    with open("output/stego_image.png", "wb") as out:
        out.write(resp.content)
    print("[OK] output/stego_image.png saved")
else:
    print("[ERR] Encode failed:", resp.text)
    raise SystemExit(1)

# ── 3. Decode ────────────────────────────────────────────────────────────────
print("[DECODE] Extracting hidden text from stego_image.png ...")

with open("output/stego_image.png", "rb") as f:
    resp2 = requests.post(
        "http://127.0.0.1:5000/decode",
        files={"image": ("stego_image.png", f, "image/png")},
        timeout=60,
    )

print("  HTTP Status:", resp2.status_code)
if resp2.status_code == 200:
    result = resp2.json()
    print("[OK] Decoded text:", result["extracted_text"])
else:
    print("[ERR] Decode failed:", resp2.text)
    raise SystemExit(1)

print("\nDone! Check output/stego_image.png and test_images/cover.png")
