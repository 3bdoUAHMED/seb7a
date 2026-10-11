"""Removes the plain white background around product photos and trims them.

Usage:  python3 prepare-products.py photo1.jpg photo2.jpg ...
        python3 prepare-products.py raw/*.jpg --out products

Each input is saved as a transparent PNG with the same name in --out
(default: products/). Only white connected to the image border is removed,
so white parts of the product itself (caps, labels) are kept.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

parser = argparse.ArgumentParser()
parser.add_argument("images", nargs="+")
parser.add_argument("--out", default=str(Path(__file__).parent / "products"))
parser.add_argument("--threshold", type=int, default=238, help="min RGB value counted as background")
args = parser.parse_args()

out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

for src in map(Path, args.images):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    # 255 where the pixel is near-white, 0 elsewhere.
    whiteish = img.convert("RGB").point(lambda v: 255 if v >= args.threshold else 0).convert("L")
    whiteish = whiteish.point(lambda v: 255 if v == 255 else 0)
    # Flood the near-white area connected to the border with 128 = background.
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if whiteish.getpixel((x, y)) == 255:
            ImageDraw.floodfill(whiteish, (x, y), 128)
    alpha = whiteish.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(alpha)
    img = img.crop(alpha.point(lambda v: 255 if v > 10 else 0).getbbox())
    dest = out_dir / (src.stem + ".png")
    img.save(dest)
    print(f"✔ {src} → {dest} ({img.width}x{img.height})")
