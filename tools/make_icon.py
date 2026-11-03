"""Draw the Memoria app icon (.ico + .png) with Pillow."""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "memoria" / "ui" / "assets"


def draw(size: int = 512) -> Image.Image:
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    bg = Image.new("RGBA", (s, s))
    top, bottom = (59, 130, 246), (29, 78, 216)
    d = ImageDraw.Draw(bg)
    for y in range(s):
        t = y / (s - 1)
        d.line([(0, y), (s, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=255)
    img.paste(bg, (0, 0), mask)
    d = ImageDraw.Draw(img)
    m = int(s * 0.2)
    d.rounded_rectangle([m, m + s * 0.04, s - m, s - m], radius=int(s * 0.06), fill=(255, 255, 255, 255))
    inner = [m + s * 0.05, m + s * 0.09, s - m - s * 0.05, s - m - s * 0.05]
    d.rounded_rectangle(inner, radius=int(s * 0.03), fill=(219, 234, 254, 255))
    x0, y0, x1, y1 = inner
    d.polygon([(x0, y1), (x0 + (x1 - x0) * 0.38, y0 + (y1 - y0) * 0.42), (x0 + (x1 - x0) * 0.62, y1)], fill=(37, 99, 235, 255))
    d.polygon([(x0 + (x1 - x0) * 0.42, y1), (x0 + (x1 - x0) * 0.7, y0 + (y1 - y0) * 0.55), (x1, y1)], fill=(96, 165, 250, 255))
    r = (x1 - x0) * 0.1
    cx, cy = x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.27
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 204, 21, 255))
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    big = draw(512)
    big.save(OUT / "memoria.png")
    big.save(OUT / "memoria.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Wrote", OUT)
