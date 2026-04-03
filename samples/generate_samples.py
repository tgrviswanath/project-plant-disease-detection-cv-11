"""
Generate sample images for cv-11 Plant Disease Detection.
Run: pip install Pillow && python generate_samples.py
Output: 6 images — healthy leaf, early blight, late blight, leaf mold,
        bacterial spot, healthy tomato.
"""
from PIL import Image, ImageDraw
import os, random

OUT = os.path.dirname(__file__)
random.seed(42)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def leaf_shape(d, cx, cy, w, h, color):
    d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=color)
    # vein
    d.line([cx, cy - h // 2, cx, cy + h // 2], fill=(int(color[0] * 0.7), int(color[1] * 0.7), int(color[2] * 0.7)), width=2)
    for angle in [-30, 30, -50, 50]:
        import math
        rad = math.radians(angle)
        ex = cx + int(w * 0.4 * math.sin(rad))
        ey = cy + int(h * 0.3 * math.cos(rad))
        d.line([cx, cy + int(h * 0.1 * (1 if angle > 0 else -1))], fill=(int(color[0] * 0.7), int(color[1] * 0.7), int(color[2] * 0.7)), width=1)


def healthy_leaf():
    img = Image.new("RGB", (400, 400), (200, 230, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 340, 340], fill=(60, 180, 60))
    d.line([200, 60, 200, 340], fill=(40, 130, 40), width=3)
    for y_off, x_off in [(-80, 60), (-40, 80), (0, 85), (40, 80), (80, 60)]:
        d.line([200, 200 + y_off, 200 + x_off, 200 + y_off - 20], fill=(40, 130, 40), width=2)
        d.line([200, 200 + y_off, 200 - x_off, 200 + y_off - 20], fill=(40, 130, 40), width=2)
    d.text((130, 360), "Healthy Leaf", fill=(40, 100, 40))
    return img


def early_blight():
    img = Image.new("RGB", (400, 400), (210, 220, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 340, 340], fill=(70, 160, 50))
    d.line([200, 60, 200, 340], fill=(50, 120, 40), width=3)
    # brown spots with yellow halo
    for sx, sy, sr in [(130, 150, 25), (240, 180, 20), (170, 250, 30), (280, 130, 18), (150, 300, 22)]:
        d.ellipse([sx - sr - 8, sy - sr - 8, sx + sr + 8, sy + sr + 8], fill=(200, 200, 60))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(100, 60, 20))
        d.ellipse([sx - sr + 5, sy - sr + 5, sx + sr - 5, sy + sr - 5], fill=(80, 40, 10))
    d.text((110, 360), "Early Blight", fill=(120, 60, 20))
    return img


def late_blight():
    img = Image.new("RGB", (400, 400), (200, 210, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 340, 340], fill=(60, 150, 50))
    # large dark water-soaked lesions
    for sx, sy, sw, sh in [(100, 120, 80, 60), (220, 200, 90, 70), (140, 260, 70, 55)]:
        d.ellipse([sx, sy, sx + sw, sy + sh], fill=(40, 80, 40))
        d.ellipse([sx + 5, sy + 5, sx + sw - 5, sy + sh - 5], fill=(20, 50, 20))
    # white mold edge
    for sx, sy, sw, sh in [(100, 120, 80, 60)]:
        d.arc([sx - 5, sy - 5, sx + sw + 5, sy + sh + 5], start=0, end=360, fill=(220, 220, 220), width=3)
    d.text((115, 360), "Late Blight", fill=(20, 80, 20))
    return img


def leaf_mold():
    img = Image.new("RGB", (400, 400), (205, 215, 195))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 340, 340], fill=(80, 160, 55))
    # yellow patches on top
    for sx, sy, sr in [(150, 140, 35), (240, 160, 28), (180, 230, 32), (260, 250, 25)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 200, 60))
    # olive/brown mold on underside (shown as darker patches)
    for sx, sy, sr in [(155, 145, 20), (245, 165, 16), (185, 235, 18)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(100, 80, 30))
    d.text((120, 360), "Leaf Mold", fill=(100, 80, 20))
    return img


def bacterial_spot():
    img = Image.new("RGB", (400, 400), (210, 225, 205))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 340, 340], fill=(65, 170, 55))
    # many small dark spots
    spots = [(r % 200 + 80, r // 200 * 15 + 100) for r in range(0, 3000, 47)]
    for sx, sy in spots[:30]:
        sr = random.randint(4, 10)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(40, 30, 10))
    d.text((100, 360), "Bacterial Spot", fill=(40, 30, 10))
    return img


def healthy_tomato():
    img = Image.new("RGB", (400, 400), (180, 220, 180))
    d = ImageDraw.Draw(img)
    # tomato fruit
    d.ellipse([100, 120, 300, 320], fill=(220, 60, 40))
    # highlight
    d.ellipse([130, 140, 190, 190], fill=(240, 120, 100))
    # stem
    d.rectangle([192, 90, 208, 130], fill=(60, 140, 40))
    # leaves at top
    d.ellipse([140, 80, 200, 130], fill=(60, 160, 50))
    d.ellipse([200, 80, 260, 130], fill=(60, 160, 50))
    d.text((110, 360), "Healthy Tomato", fill=(40, 100, 40))
    return img


if __name__ == "__main__":
    print("Generating cv-11 samples...")
    save(healthy_leaf(), "sample_healthy_leaf.jpg")
    save(early_blight(), "sample_early_blight.jpg")
    save(late_blight(), "sample_late_blight.jpg")
    save(leaf_mold(), "sample_leaf_mold.jpg")
    save(bacterial_spot(), "sample_bacterial_spot.jpg")
    save(healthy_tomato(), "sample_healthy_tomato.jpg")
    print("Done — 6 images in samples/")
