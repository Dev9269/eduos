"""Generate EduOS branding PNG images."""

import struct, zlib, math, os


def create_png(w, h, pix, path):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            r, g, b, a = pix(x, y, w, h)
            raw.extend(struct.pack("BBBB", r, g, b, a))

    def ck(ct, d):
        c = ct + d
        return (
            struct.pack(">I", len(d))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(ck(b"IHDR", ihdr))
        f.write(ck(b"IDAT", zlib.compress(bytes(raw))))
        f.write(ck(b"IEND", b""))
    print(f"  {path} ({w}x{h})")


def logo_px(x, y, w, h):
    cx, cy = w // 2, h // 2
    d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    if d < 60:
        return (37, 99, 235, 255)
    if d > 65 and d < 80:
        return (16, 185, 129, 255)
    return (10, 22, 40, 0)


def dark_px(x, y, w, h):
    return (10, 22, 40, 255)


def grad_px(x, y, w, h):
    v = int(40 - 30 * (y / h))
    return (v, v + 10, v + 20, 255)


def run():
    os.makedirs("branding/plymouth/edos-plymouth-theme", exist_ok=True)
    os.makedirs("branding/sddm", exist_ok=True)
    os.makedirs("branding/grub", exist_ok=True)
    os.makedirs("themes/edos-dark/wallpapers/EduOSDark/contents/images", exist_ok=True)
    os.makedirs("packages/eduos-branding/usr/share/plymouth/themes/edos", exist_ok=True)

    print("Generating branding images...")
    create_png(64, 64, logo_px, "branding/plymouth/edos-plymouth-theme/logo.png")
    create_png(128, 128, logo_px, "branding/sddm/logo.png")
    create_png(1024, 768, grad_px, "branding/grub/background.png")
    create_png(
        1920,
        1080,
        dark_px,
        "themes/edos-dark/wallpapers/EduOSDark/contents/images/1920x1080.png",
    )
    create_png(
        256,
        256,
        logo_px,
        "packages/eduos-branding/usr/share/plymouth/themes/edos/logo.png",
    )
    print("All images generated!")


if __name__ == "__main__":
    run()
