"""Builds offer-3 wide backgrounds from products/offer3-bg-clean.jpg (the supplied
800x200 photo with its products erased). Products are drawn back on top in HTML at
the same spots (see STUDIO_GEO in banners.js), so the erased areas stay covered."""
from pathlib import Path
from PIL import Image, ImageOps
here = Path(__file__).parent
src = Image.open(here / "products/offer3-bg-clean.jpg").convert("RGB")

def build(name, W, H, k, ox, oy):
    s = src.resize((round(800 * k), round(200 * k)), Image.LANCZOS)
    c = Image.new("RGB", (W, H))
    # fill any gap on the left / top with mirrored copies of the photo
    c.paste(ImageOps.mirror(s), (ox - s.width, oy))
    c.paste(ImageOps.flip(s), (ox, oy - s.height))
    c.paste(ImageOps.flip(ImageOps.mirror(s)), (ox - s.width, oy - s.height))
    c.paste(s, (ox, oy))
    c.save(here / f"products/offer3-bg-{name}.jpg", quality=93)

build("800x200", 800, 200, 1.0, 0, 0)
build("1440x300", 1440, 300, 1.5, 240, 0)
build("706x320", 706, 320, 1.25, 0, 70)
