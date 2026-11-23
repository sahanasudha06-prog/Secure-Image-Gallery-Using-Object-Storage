import io
import math
import random
from PIL import Image, ImageDraw
from storage_service import StorageService

def generate_layer_data_lake():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    # Background Grid
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=(30, 41, 59), width=1)
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=(30, 41, 59), width=1)

    # 3D Tiered Cylinders / Data Lake Disks
    colors = [(239, 68, 68), (249, 115, 22), (59, 130, 246), (16, 185, 129)]
    y_starts = [550, 430, 310, 190]
    labels = ["Version 1.0 (Base Archive)", "Version 1.1 (Delta Updates)", "Version 2.0 (Verified SSE-S3)", "Version 2.1 (Active Latest)"]

    for i in range(4):
        y = y_starts[i]
        c = colors[i]
        # cylinder side
        draw.rectangle([400, y - 40, 800, y + 20], fill=c)
        # bottom ellipse
        draw.ellipse([400, y, 800, y + 40], fill=(int(c[0]*0.7), int(c[1]*0.7), int(c[2]*0.7)))
        # top ellipse
        draw.ellipse([400, y - 60, 800, y - 20], fill=c, outline="#ffffff", width=2)
        # label
        draw.text((830, y - 45), labels[i], fill="#f8fafc")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def update_all_visuals():
    storage = StorageService()
    # Replace plain versioning banner with rich 3D data lake
    buf = generate_layer_data_lake()
    storage.upload_image(buf, "versioning_data_lake.jpg", "image/jpeg", category="Cloud & Security")
    print("Updated versioning_data_lake.jpg with rich visual")

if __name__ == "__main__":
    update_all_visuals()
