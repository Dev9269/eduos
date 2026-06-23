#!/usr/bin/env python3
"""
EduOS Original Wallpaper Generator
Creates 4 unique wallpapers (1920x1080) using PIL with geometric patterns,
gradients, and EduOS branding. No external images used.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUTPUT_DIR = Path(__file__).parent
W, H = 1920, 1080


def hex_to_rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw, w, h, c1, c2, vertical=True):
    """Draw a linear gradient."""
    for i in range(h if vertical else w):
        t = i / (h if vertical else w)
        c = lerp_color(c1, c2, t)
        if vertical:
            draw.line([(0, i), (w, i)], fill=c)
        else:
            draw.line([(i, 0), (i, h)], fill=c)


def draw_circle(draw, cx, cy, r, fill=None, outline=None, width=0):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)


def draw_rounded_rect(draw, x, y, w, h, r, fill):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill)


# ─── WALLPAPER 1: EduOS Default ───────────────────────────────────────────────
def generate_default():
    img = Image.new('RGBA', (W, H))
    draw = ImageDraw.Draw(img)

    c1, c2, c3 = hex_to_rgb('#1a1a2e'), hex_to_rgb('#16213e'), hex_to_rgb('#0f3460')
    draw_gradient(draw, W, H, c1, c3)

    # Large translucent circles
    draw_circle(draw, int(W*0.15), int(H*0.3), 280, fill=(233, 69, 96, 12))
    draw_circle(draw, int(W*0.85), int(H*0.7), 350, fill=(15, 52, 96, 15))
    draw_circle(draw, int(W//2), int(H//2), 500, fill=(83, 52, 131, 6))

    # Hexagonal grid
    hex_size = 50
    color = (255, 255, 255, 6)
    for row in range(-hex_size, H + hex_size, int(hex_size * 1.8)):
        offset = hex_size * 1.5 if (row // int(hex_size * 1.8)) % 2 == 0 else 0
        for col in range(-hex_size, W + hex_size, hex_size * 3):
            cx = col + offset
            for angle in range(6):
                a1 = math.radians(angle * 60)
                a2 = math.radians((angle + 1) * 60)
                x1 = int(cx + math.cos(a1) * hex_size)
                y1 = int(row + math.sin(a1) * hex_size)
                x2 = int(cx + math.cos(a2) * hex_size)
                y2 = int(row + math.sin(a2) * hex_size)
                draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Circuit nodes and connections
    nodes = [(int(W*0.1), int(H*0.2)), (int(W*0.25), int(H*0.15)),
             (int(W*0.4), int(H*0.3)), (int(W*0.6), int(H*0.7)),
             (int(W*0.75), int(H*0.8)), (int(W*0.9), int(H*0.6)),
             (int(W*0.3), int(H*0.6)), (int(W*0.5), int(H*0.4)),
             (int(W*0.7), int(H*0.3))]
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes[i+1:], i+1):
            d = math.hypot(x2-x1, y2-y1)
            if d < W * 0.5:
                alpha = int(15 * (1 - d / (W * 0.5)))
                draw.line([(x1, y1), (x2, y2)], fill=(233, 69, 96, alpha), width=1)

    for nx, ny in nodes:
        draw_circle(draw, nx, ny, 3, fill=(233, 69, 96, 180))

    # Central "E" mark
    ew, eh = 180, 220
    ex, ey = W//2 - ew//2, H//2 - eh//2 - 30
    accent = (233, 69, 96, 35)
    draw_rounded_rect(draw, ex, ey, ew, 18, 4, accent)
    draw_rounded_rect(draw, ex, ey + eh//2 - 9, ew, 18, 4, accent)
    draw_rounded_rect(draw, ex, ey + eh - 18, ew, 18, 4, accent)
    draw_rounded_rect(draw, ex + ew - 36, ey + 18, 36, eh//2 - 27, 4, accent)
    draw_rounded_rect(draw, ex + ew - 36, ey + eh//2 + 9, 36, eh//2 - 27, 4, accent)

    # Central glow rings
    for r in range(130, 30, -15):
        a = 8 if r < 70 else 4
        draw_circle(draw, W//2, H//2, r, outline=(233, 69, 96, a), width=1)

    # Text watermark
    try:
        fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        fnt_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        fnt_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        fnt_title = ImageFont.load_default()
        fnt_sub = fnt_footer = fnt_title

    # Title
    _, _, tw, th = draw.textbbox((0, 0), "EDUOS", font=fnt_title)
    draw.text(((W - tw) // 2, H // 2 + 70), "EDUOS", fill=(255, 255, 255, 160), font=fnt_title)

    _, _, sw, sh = draw.textbbox((0, 0), "ENGINEERING EDUCATION", font=fnt_sub)
    draw.text(((W - sw) // 2, H // 2 + 70 + th + 10), "ENGINEERING EDUCATION",
              fill=(233, 69, 96, 140), font=fnt_sub)

    _, _, fw, fh = draw.textbbox((0, 0), "EDUCATION EDITION 2026", font=fnt_footer)
    draw.text(((W - fw) // 2, H - 40), "EDUCATION EDITION 2026",
              fill=(255, 255, 255, 40), font=fnt_footer)

    return img


# ─── WALLPAPER 2: EduOS Dark ──────────────────────────────────────────────────
def generate_dark():
    img = Image.new('RGBA', (W, H))
    draw = ImageDraw.Draw(img)

    c1, c2 = hex_to_rgb('#0a0a0a'), hex_to_rgb('#1a1a2e')
    draw_gradient(draw, W, H, c1, c2)

    # Glowing concentric rings
    for r in range(350, 80, -20):
        a = max(2, int(18 * (1 - r / 350)))
        draw_circle(draw, W // 2, H // 2, r, outline=(83, 52, 131, a), width=1)

    # Dotted wave patterns
    for i in range(40):
        dx = int(W * 0.05 + (W * 0.9) * (i / 40))
        dy = int(H * 0.15 + math.sin(i * 0.7) * 40)
        draw_circle(draw, dx, dy, 2, fill=(255, 255, 255, 25))
        dy2 = int(H * 0.85 + math.sin(i * 0.7 + 1) * 40)
        draw_circle(draw, dx, dy2, 2, fill=(255, 255, 255, 25))

    # Terminal-style lines
    green = (0, 255, 136, 60)
    lines = [
        (f"./eduos --init", H * 0.40),
        ("> Loading kernel modules...", H * 0.44),
        ("> Initializing subsystems...", H * 0.47),
        ("> System ready.", H * 0.50),
        ("> EDUOS v2026.06", H * 0.53),
        ("_", H * 0.57),
    ]
    try:
        fnt_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
    except Exception:
        fnt_code = ImageFont.load_default()

    for text, y_pos in lines:
        _, _, tw, th = draw.textbbox((0, 0), text, font=fnt_code)
        draw.text((int(W * 0.1), int(y_pos)), text, fill=green, font=fnt_code)

    # Corner brackets
    m, bs = 40, 50
    accent = (233, 69, 96, 80)
    corners = [
        (m, m, m+bs, m, m, m, m, m+bs),
        (W-m, m, W-m-bs, m, W-m, m, W-m, m+bs),
        (m, H-m, m+bs, H-m, m, H-m, m, H-m-bs),
        (W-m, H-m, W-m-bs, H-m, W-m, H-m, W-m, H-m-bs),
    ]
    for x1, y1, x2, y2, x3, y3, x4, y4 in corners:
        draw.line([(x1, y1), (x2, y2)], fill=accent, width=2)
        draw.line([(x3, y3), (x4, y4)], fill=accent, width=2)

    # Title
    try:
        fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        fnt_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        fnt_title = fnt_sub = ImageFont.load_default()

    _, _, tw, th = draw.textbbox((0, 0), "EDUOS", font=fnt_title)
    draw.text(((W - tw) // 2, int(H * 0.20)), "EDUOS", fill=(255, 255, 255, 200), font=fnt_title)
    _, _, sw, sh = draw.textbbox((0, 0), "DARK EDITION", font=fnt_sub)
    draw.text(((W - sw) // 2, int(H * 0.20) + th + 8), "DARK EDITION",
              fill=(233, 69, 96, 130), font=fnt_sub)

    return img


# ─── WALLPAPER 3: EduOS Light ─────────────────────────────────────────────────
def generate_light():
    img = Image.new('RGBA', (W, H))
    draw = ImageDraw.Draw(img)

    c1, c2 = hex_to_rgb('#f8f9fa'), hex_to_rgb('#e9ecef')
    draw_gradient(draw, W, H, c1, c2, vertical=False)

    # Dots grid
    spacing = 40
    for gy in range(0, H, spacing):
        offset = 5 if (gy // spacing) % 2 == 0 else 0
        for gx in range(offset, W, spacing):
            draw_circle(draw, gx, gy, 1.5, fill=(173, 181, 189, 25))

    # Large circle accents
    draw_circle(draw, int(W*0.8), int(H*0.2), 220, fill=(37, 99, 235, 8))
    draw_circle(draw, int(W*0.2), int(H*0.8), 180, fill=(37, 99, 235, 6))

    # Thin horizontal lines
    draw.line([(int(W*0.1), int(H*0.47)), (int(W*0.4), int(H*0.47))],
              fill=(37, 99, 235, 30), width=1)
    draw.line([(int(W*0.6), int(H*0.53)), (int(W*0.9), int(H*0.53))],
              fill=(37, 99, 235, 30), width=1)

    # Diamond center
    cx, cy, sz = W//2, H//2 - 50, 70
    diamond = [(cx, cy - sz), (cx + sz, cy), (cx, cy + sz), (cx - sz, cy)]
    for i in range(4):
        draw.line([diamond[i], diamond[(i+1) % 4]], fill=(37, 99, 235, 60), width=2)
    draw_circle(draw, cx, cy, 6, fill=(37, 99, 235, 60))

    # Text
    try:
        fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        fnt_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        fnt_title = fnt_sub = ImageFont.load_default()

    _, _, tw, th = draw.textbbox((0, 0), "EDUOS", font=fnt_title)
    draw.text(((W - tw) // 2, cy + sz + 30), "EDUOS", fill=(33, 37, 41, 160), font=fnt_title)
    _, _, sw, sh = draw.textbbox((0, 0), "LIGHT EDITION", font=fnt_sub)
    draw.text(((W - sw) // 2, cy + sz + 30 + th + 6), "LIGHT EDITION",
              fill=(108, 117, 125, 100), font=fnt_sub)

    return img


# ─── WALLPAPER 4: EduOS Minimal ───────────────────────────────────────────────
def generate_minimal():
    img = Image.new('RGBA', (W, H))
    draw = ImageDraw.Draw(img)

    c1, c2 = hex_to_rgb('#0f172a'), hex_to_rgb('#1e293b')
    draw_gradient(draw, W, H, c1, c2)

    # Single horizontal line
    draw.line([(int(W*0.15), H//2), (int(W*0.85), H//2)],
              fill=(233, 69, 96, 60), width=1)

    # Accent dot
    draw_circle(draw, W//2, H//2, 4, fill=(233, 69, 96, 180))

    # Title
    try:
        fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        fnt_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        fnt_mark = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        fnt_title = fnt_sub = fnt_mark = ImageFont.load_default()

    _, _, tw, th = draw.textbbox((0, 0), "EDUOS", font=fnt_title)
    draw.text(((W - tw) // 2, H//2 - th - 30), "EDUOS", fill=(255, 255, 255, 200), font=fnt_title)

    _, _, sw, sh = draw.textbbox((0, 0), "MINIMAL", font=fnt_sub)
    draw.text(((W - sw) // 2, H//2 + 15), "MINIMAL",
              fill=(233, 69, 96, 120), font=fnt_sub)

    # Bottom-right corner mark
    mx, my, mk = W - 50, H - 50, 60
    draw.line([(mx - mk, my), (mx, my)], fill=(255, 255, 255, 15), width=1)
    draw.line([(mx, my), (mx, my - mk)], fill=(255, 255, 255, 15), width=1)

    _, _, mw, mh = draw.textbbox((0, 0), "EDUOS 2026", font=fnt_mark)
    draw.text((mx - mw - 5, my - mk + 5), "EDUOS 2026",
              fill=(255, 255, 255, 18), font=fnt_mark)

    return img


# ─── GENERATE ALL ──────────────────────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wallpapers = [
        ("eduos-wallpaper-default.png", generate_default, "Default"),
        ("eduos-wallpaper-dark.png", generate_dark, "Dark"),
        ("eduos-wallpaper-light.png", generate_light, "Light"),
        ("eduos-wallpaper-minimal.png", generate_minimal, "Minimal"),
    ]

    for fname, gen_func, label in wallpapers:
        path = OUTPUT_DIR / fname
        print(f"Generating {label}...", flush=True)
        img = gen_func()
        img.save(str(path), "PNG")
        size_kb = path.stat().st_size / 1024
        print(f"  => Saved: {path} ({size_kb:.1f} KB)", flush=True)

    print("\nAll wallpapers generated successfully!", flush=True)


if __name__ == "__main__":
    main()
