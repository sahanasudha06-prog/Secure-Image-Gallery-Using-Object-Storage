import io
import math
import random
from PIL import Image, ImageDraw
from storage_service import StorageService

def generate_golden_sunset():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    # Sky Gradient: Deep violet to fiery orange to golden yellow
    for y in range(h):
        r = int(30 + (245 - 30) * (y / h))
        g = int(20 + (140 - 20) * (y / h))
        b = int(60 + (30 - 60) * (y / h))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Glowing Sun
    sun_x, sun_y, sun_r = 600, 420, 110
    for r in range(sun_r + 60, sun_r, -2):
        alpha_color = (255, 200, 80)
        draw.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r], fill=alpha_color)
    draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(255, 245, 180))

    # Mountains silhouette in background
    points1 = [(0, 520)]
    for x in range(0, w + 40, 40):
        y = 480 + int(70 * math.sin(x * 0.008) + 40 * math.cos(x * 0.02))
        points1.append((x, y))
    points1.extend([(w, h), (0, h)])
    draw.polygon(points1, fill=(80, 25, 45))

    # Closer Mountain Ridge
    points2 = [(0, 580)]
    for x in range(0, w + 30, 30):
        y = 560 + int(60 * math.sin(x * 0.015) + 30 * math.sin(x * 0.03))
        points2.append((x, y))
    points2.extend([(w, h), (0, h)])
    draw.polygon(points2, fill=(35, 12, 25))

    # Foreground Lake Reflection
    draw.rectangle([0, 640, w, h], fill=(20, 8, 15))
    for y in range(640, h, 8):
        offset = int(40 * math.sin(y * 0.05))
        draw.line([sun_x - 140 + offset, y, sun_x + 140 + offset, y], fill=(240, 160, 50), width=3)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def generate_cyberpunk_neon():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (10, 5, 25))
    draw = ImageDraw.Draw(img)

    # Dark gradient background
    for y in range(500):
        ratio = y / 500
        r = int(15 + 40 * ratio)
        g = int(5 + 10 * ratio)
        b = int(35 + 80 * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Giant Retro Synth Sun
    cx, cy, radius = 600, 340, 140
    for y in range(cy - radius, cy + radius):
        dx = int(math.sqrt(max(0, radius**2 - (y - cy)**2)))
        # Horizontal stripes
        if (y // 10) % 2 == 0 or y < cy:
            ratio = (y - (cy - radius)) / (2 * radius)
            r = int(255 - 40 * ratio)
            g = int(60 + 160 * ratio)
            b = int(180)
            draw.line([(cx - dx, y), (cx + dx, y)], fill=(r, g, b))

    # Perspective Grid Horizon
    draw.rectangle([0, 500, w, h], fill=(8, 4, 18))
    vp_x, vp_y = 600, 500

    # Grid vertical perspective lines
    for x in range(-400, w + 500, 60):
        draw.line([(vp_x, vp_y), (x, h)], fill=(168, 85, 247), width=2)

    # Horizontal grid lines with increasing spacing
    y_step = 505
    spacing = 4
    while y_step < h:
        draw.line([(0, y_step), (w, y_step)], fill=(6, 182, 212), width=2)
        y_step += spacing
        spacing = int(spacing * 1.3)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def generate_deep_space_nebula():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (4, 6, 16))
    draw = ImageDraw.Draw(img)

    # Cosmic Dust Clouds
    random.seed(42)
    for _ in range(120):
        cx = random.randint(200, 1000)
        cy = random.randint(150, 650)
        cr = random.randint(80, 240)
        color = random.choice([
            (79, 70, 229, 20),
            (236, 72, 153, 15),
            (56, 189, 248, 18),
            (168, 85, 247, 22)
        ])
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=color[:3])

    # Starfield
    for _ in range(400):
        sx = random.randint(0, w)
        sy = random.randint(0, h)
        brightness = random.randint(160, 255)
        sz = random.choice([1, 1, 1, 2, 3])
        draw.ellipse([sx, sy, sx + sz, sy + sz], fill=(brightness, brightness, 255))

    # Ringed Planet
    px, py, pr = 880, 240, 70
    draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(225, 140, 80))
    # Planet Rings
    for ro in range(pr + 25, pr + 60, 4):
        draw.arc([px - ro - 60, py - ro // 2, px + ro + 60, py + ro // 2], start=10, end=170, fill=(240, 190, 120), width=2)
        draw.arc([px - ro - 60, py - ro // 2, px + ro + 60, py + ro // 2], start=190, end=350, fill=(240, 190, 120), width=2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def generate_emerald_mist_forest():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    # Misty Green Gradient Sky
    for y in range(h):
        ratio = y / h
        r = int(12 + 20 * ratio)
        g = int(35 + 65 * ratio)
        b = int(30 + 40 * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Crescent Moon
    draw.ellipse([260, 140, 360, 240], fill=(230, 245, 235))
    draw.ellipse([290, 130, 390, 240], fill=(16, 45, 38))

    # Distant Pine Trees layer
    def draw_pine_tree(x, base_y, tree_h, tree_w, fill_color):
        points = [
            (x, base_y - tree_h),
            (x - tree_w // 2, base_y),
            (x + tree_w // 2, base_y)
        ]
        draw.polygon(points, fill=fill_color)

    # Layer 1 (Distant)
    for x in range(0, w + 40, 35):
        h_tree = random.randint(180, 280)
        draw_pine_tree(x, 620, h_tree, 60, (18, 55, 45))

    # Mist Band 1
    draw.rectangle([0, 580, w, 660], fill=(25, 75, 60))

    # Layer 2 (Mid-ground)
    for x in range(15, w + 40, 50):
        h_tree = random.randint(260, 380)
        draw_pine_tree(x, 740, h_tree, 90, (10, 38, 30))

    # Mist Band 2 & Foreground
    draw.rectangle([0, 710, w, h], fill=(6, 25, 20))
    for x in range(30, w + 60, 70):
        h_tree = random.randint(340, 480)
        draw_pine_tree(x, h + 30, h_tree, 130, (4, 18, 14))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def generate_cloud_security_core():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (11, 15, 25))
    draw = ImageDraw.Draw(img)

    # Glowing radial grid
    cx, cy = 600, 400
    for r in range(80, 500, 60):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#1e293b", width=1)

    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x2 = cx + int(480 * math.cos(rad))
        y2 = cy + int(480 * math.sin(rad))
        draw.line([(cx, cy), (x2, y2)], fill="#1e293b", width=1)

    # Futuristic Hexagonal Shield in Center
    shield_points = [
        (600, 220),
        (760, 300),
        (760, 480),
        (600, 580),
        (440, 480),
        (440, 300)
    ]
    draw.polygon(shield_points, fill="#0f172a", outline="#6366f1")

    # Inner Glow Shield
    inner_points = [
        (600, 250),
        (730, 320),
        (730, 460),
        (600, 550),
        (470, 460),
        (470, 320)
    ]
    draw.polygon(inner_points, fill="#1e1b4b", outline="#818cf8")

    # AWS Cloud S3 Lock Core
    draw.ellipse([540, 350, 660, 470], fill="#312e81", outline="#38bdf8", width=3)
    draw.rectangle([570, 410, 630, 460], fill="#38bdf8", outline="#ffffff", width=2)
    draw.arc([580, 385, 620, 425], start=180, end=360, fill="#38bdf8", width=4)

    # Data Streams / Nodes
    nodes = [
        (300, 260, "IAM Role: EC2-S3"),
        (900, 260, "S3 Bucket: Private"),
        (300, 540, "SigV4 Pre-signed"),
        (900, 540, "Versioning Active")
    ]
    for nx, ny, label in nodes:
        draw.line([(cx, cy), (nx, ny)], fill="#4f46e5", width=2)
        draw.ellipse([nx - 24, ny - 24, nx + 24, ny + 24], fill="#1e293b", outline="#10b981", width=2)
        draw.text((nx - 60, ny + 32), label, fill="#cbd5e1")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def generate_modern_architecture():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), (245, 240, 235))
    draw = ImageDraw.Draw(img)

    # Minimalist Architectural Sky
    for y in range(h):
        val = int(240 - 30 * (y / h))
        draw.line([(0, y), (w, y)], fill=(val, val + 5, val + 15))

    # Skyscraper Facade Geometric Polygons
    # Tower 1
    t1 = [(150, h), (150, 200), (450, 80), (450, h)]
    draw.polygon(t1, fill=(40, 55, 75))
    # Facade glass panels
    for gy in range(120, h, 28):
        draw.line([(180, gy), (420, gy - 35)], fill=(70, 95, 125), width=2)

    # Tower 2 (Glass reflection)
    t2 = [(450, h), (450, 80), (750, 180), (750, h)]
    draw.polygon(t2, fill=(210, 110, 80))
    for gy in range(120, h, 35):
        draw.line([(470, gy), (730, gy + 30)], fill=(235, 140, 110), width=2)

    # Tower 3
    t3 = [(750, h), (750, 180), (1050, 280), (1050, h)]
    draw.polygon(t3, fill=(30, 42, 58))
    for gy in range(210, h, 25):
        draw.line([(770, gy), (1030, gy + 25)], fill=(55, 75, 100), width=2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf

def seed_rich_gallery():
    storage = StorageService()
    
    artworks = [
        ("golden_sunset_peaks.jpg", generate_golden_sunset, "Nature"),
        ("cyberpunk_neon_horizon.jpg", generate_cyberpunk_neon, "Abstract"),
        ("deep_space_nebula.jpg", generate_deep_space_nebula, "Wallpapers"),
        ("emerald_mist_forest.jpg", generate_emerald_mist_forest, "Nature"),
        ("cloud_security_architecture.jpg", generate_cloud_security_core, "Cloud & Security"),
        ("modern_geometric_skyline.jpg", generate_modern_architecture, "Architecture")
    ]

    for filename, generator_func, category in artworks:
        buf = generator_func()
        res = storage.upload_image(buf, filename, "image/jpeg")
        print(f"Uploaded high-res artwork: {filename} [{category}] - Version {res['version_id']}")

if __name__ == "__main__":
    seed_rich_gallery()
