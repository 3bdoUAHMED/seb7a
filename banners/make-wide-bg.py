"""Builds the wide-banner backgrounds for offer 3 from products/offer3-wide-src.jpg (800x200)."""
from pathlib import Path
from PIL import Image, ImageFilter
here = Path(__file__).parent
src = Image.open(here / "products/offer3-wide-src.jpg").convert("RGB")

# 800 x 200: as is
src.save(here / "products/offer3-bg-800x200.jpg", quality=93)

# 1440 x 300: scale x1.8, crop vertically
big = src.resize((1440, 360), Image.LANCZOS)
big.crop((0, 18, 1440, 318)).save(here / "products/offer3-bg-1440x300.jpg", quality=93)

# 706 x 320: wall from the empty left part, products band on the right, logo top-left
wall = src.crop((0, 0, 245, 200)).resize((706, 320), Image.LANCZOS)
band = src.crop((240, 0, 578, 200))          # the three products
k = 1.3
band = band.resize((int(band.width * k), int(band.height * k)), Image.LANCZOS)
mask = Image.new("L", band.size, 255)
fe = 36
px = mask.load()
for y in range(band.height):
    for x in range(band.width):
        v = 255
        if x < fe: v = min(v, int(255 * x / fe))
        if band.width - 1 - x < fe: v = min(v, int(255 * (band.width - 1 - x) / fe))
        if y < fe: v = min(v, int(255 * y / fe))
        px[x, y] = v
canvas = wall.copy()
ox, oy = 706 - band.width + 8, 320 - band.height
canvas.paste(band, (ox, oy), mask)
logo = src.crop((626, 18, 784, 68))
lm = Image.new("L", logo.size, 0)
# keep only the red/dark logo pixels so the wall behind blends in
lp, mp = logo.load(), lm.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b = lp[x, y]
        if r - g > 40 or r < 150 or g - r > 10:
            mp[x, y] = 255
lm = lm.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
canvas.paste(logo, (20, 18), lm)
canvas.save(here / "products/offer3-bg-706x320.jpg", quality=93)
print(band.size, ox, oy)
