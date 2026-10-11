"""Removes the plain white background around product photos and trims them.

Usage:  python3 prepare-products.py photo1.jpg photo2.jpg ...
        python3 prepare-products.py raw/*.jpg --out products

Each input is saved as a transparent PNG with the same name in --out
(default: products/). Only background outside the product outline is removed, so white
bottles, caps and labels are kept.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

parser = argparse.ArgumentParser()
parser.add_argument("images", nargs="+")
parser.add_argument("--out", default=str(Path(__file__).parent / "products"))
parser.add_argument("--threshold", type=int, default=252, help="pixels with any channel below this count as product")
parser.add_argument("--close", type=int, default=7, help="gap size (odd px) closed in the product outline")
args = parser.parse_args()

out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

for src in map(Path, args.images):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    # Mark everything that is clearly not background, close small gaps in the
    # outline, then treat any area the border can't reach as part of the
    # product. This keeps white bottles and labels intact.
    gray = img.convert("RGB").point(lambda v: 255 if v < args.threshold else 0).convert("L")
    product = gray.point(lambda v: 255 if v else 0).filter(ImageFilter.MaxFilter(args.close))
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if product.getpixel((x, y)) == 0:
            ImageDraw.floodfill(product, (x, y), 128)
    # Erode a little past the closing so light anti-aliased edge pixels go too.
    alpha = product.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.MinFilter(args.close + 4))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(alpha)
    img = img.crop(alpha.point(lambda v: 255 if v > 10 else 0).getbbox())
    dest = out_dir / (src.stem + ".png")
    img.save(dest)
    print(f"✔ {src} → {dest} ({img.width}x{img.height})")
