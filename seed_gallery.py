import io
from PIL import Image, ImageDraw, ImageFont
from storage_service import StorageService

def create_sample_banner(filename, title, subtitle, bg_color1, bg_color2):
    width, height = 800, 500
    img = Image.new("RGB", (width, height), bg_color1)
    draw = ImageDraw.Draw(img)

    # Subtle gradient or grid pattern
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=bg_color2, width=1)
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=bg_color2, width=1)

    # Card box
    draw.rectangle([100, 120, 700, 380], fill="#0f172a", outline="#334155", width=2)
    draw.text((140, 170), title, fill="#ffffff")
    draw.text((140, 220), subtitle, fill="#94a3b8")
    draw.text((140, 280), "Encrypted at Rest: AES-256 | S3 Private Object", fill="#34d399")
    draw.text((140, 310), "Owner: Sahana & Samudyata | Group: ImageAdmins", fill="#818cf8")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def seed():
    storage = StorageService()
    samples = [
        ("cloud_architecture_overview.jpg", "CLOUD ARCHITECTURE", "AWS EC2 + Amazon S3 Object Storage", "#1e1b4b", "#312e81"),
        ("security_policy_enforcement.jpg", "IAM LEAST PRIVILEGE", "Role: EC2-S3-ImageGallery-Role", "#064e3b", "#065f46"),
        ("pre_signed_token_demo.jpg", "PRE-SIGNED SECURE URL", "SigV4 Time-Bounded Access Delegation", "#1e293b", "#334155"),
        ("versioning_data_lake.jpg", "BUCKET VERSIONING", "Immutability & Accidental Deletion Protection", "#450a0a", "#7f1d1d")
    ]

    for filename, title, sub, c1, c2 in samples:
        buf = create_sample_banner(filename, title, sub, c1, c2)
        res = storage.upload_image(buf, filename, "image/jpeg")
        print(f"Seeded: {filename} (Version: {res['version_id']})")

if __name__ == "__main__":
    seed()
