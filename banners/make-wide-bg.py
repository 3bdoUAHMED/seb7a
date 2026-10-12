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

# 800 x 1200 (vertical): the supplied vertical photo cut above the old tapes,
# with a stone step face below for the button.
v = Image.open(here / "products/offer3-vertical-src.png").convert("RGB")
cut = 926
canvas = Image.new("RGB", (800, 1200))
canvas.paste(v.crop((0, 0, 800, cut)), (0, 0))
st = Image.open(here / "products/offer3-stone.jpg").convert("RGB")
stone = Image.new("RGB", (800, 274))
for i, y in enumerate(range(0, 274, st.height)):
    stone.paste(st.crop((i * 400, 0, i * 400 + 800, st.height)), (0, y))
import numpy as np
s = np.asarray(stone).astype(np.float32)
grad = np.linspace(1.0, 0.86, s.shape[0])[:, None, None]
s = s * grad
s[:3] = s[:3] * 1.06          # bright top edge of the step
s[3:14] *= np.linspace(0.85, 1, 11)[:, None, None]   # contact shadow just under the edge
canvas.paste(Image.fromarray(s.clip(0, 255).astype(np.uint8)), (0, cut))
canvas.save(here / "products/offer3-bg-800x1200.jpg", quality=93)
