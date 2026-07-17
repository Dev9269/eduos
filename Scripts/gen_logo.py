#!/usr/bin/env python3
"""Generate EduOS branding images: logo, grub background, wallpaper, sddm logo, plymouth logo."""

import struct, zlib, math, os


def create_png(width, height, pixels_func, filepath):
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            r, g, b, a = pixels_func(x, y, width, height)
            raw += struct.pack("BBBB", r, g, b, a)

    def chunk(ctype, data):
        c = ctype + data
        return (
            struct.pack(">I", len(data))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    with open(filepath, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(raw)))
        f.write(chunk(b"IEND", b""))
    print(f"Generated {filepath} ({width}x{height})")


def eduos_logo_pixels(x, y, w, h):
    cx, cy = w // 2, h // 2
    dx, dy = x - cx, y - cy
    d = math.sqrt(dx * dx + dy * dy)
    if d < 60:
        return 37, 99, 235, 255
    if d < 80 and d > 65:
        return 16, 185, 129, 255
    if abs(x - w // 2) < 40 and y > int(h * 0.62) and y < int(h * 0.78):
        return 37, 99, 235, 255
    return 10, 22, 40, 0


def grub_background_pixels(x, y, w, h):
    t = y / h
    r = int(10 + (15 - 10) * t)
    g = int(22 + (32 - 22) * t)
    b = int(40 + (68 - 40) * t)
    return r, g, b, 255


def wallpaper_pixels(x, y, w, h):
    t = y / h
    r = int(15 + (10 - 15) * t)
    g = int(32 + (22 - 32) * t)
    b = int(68 + (40 - 68) * t)
    cx, cy = w // 2, h // 2
    dx, dy = x - cx, y - cy
    d = math.sqrt(dx * dx + dy * dy)
    if d < 60:
        return 37, 99, 235, 255
    return r, g, b, 255


def sddm_logo_pixels(x, y, w, h):
    cx, cy = w // 2, h // 2
    dx, dy = x - cx, y - cy
    d = math.sqrt(dx * dx + dy * dy)
    if d < 28:
        return 37, 99, 235, 255
    if d < 38 and d > 30:
        return 16, 185, 129, 255
    if abs(x - w // 2) < 18 and y > int(h * 0.6) and y < int(h * 0.78):
        return 37, 99, 235, 255
    return 10, 22, 40, 0


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    create_png(
        256,
        256,
        eduos_logo_pixels,
        os.path.join(base, "branding", "plymouth", "edos-plymouth-theme", "logo.png"),
    )
    create_png(
        1024,
        768,
        grub_background_pixels,
        os.path.join(base, "branding", "grub", "background.png"),
    )
    create_png(
        1920,
        1080,
        wallpaper_pixels,
        os.path.join(
            base, "themes", "edos-dark", "wallpapers", "EduOSDark", "wallpaper.png"
        ),
    )
    create_png(
        128, 128, sddm_logo_pixels, os.path.join(base, "branding", "sddm", "logo.png")
    )
    create_png(
        256,
        256,
        eduos_logo_pixels,
        os.path.join(base, "branding", "plymouth", "edos-plymouth-theme", "logo.png"),
    )
    print("\nAll branding images generated successfully.")
