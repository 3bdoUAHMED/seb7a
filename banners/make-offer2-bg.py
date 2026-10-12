"""Wide backgrounds for offer 2: the podium group from products/offer2-podium.jpg
placed on a wall extended from the photo's own edge colours."""
from pathlib import Path
from PIL import Image
import numpy as np
here = Path(__file__).parent
ph = Image.open(here / "products/offer2-podium.jpg").convert("RGB")
A = np.asarray(ph).astype(np.float32)
crop = (40, 382, 760, 1075)            # pen top .. podium base
cw, ch = crop[2] - crop[0], crop[3] - crop[1]

def build(name, W, H, cx, pad=6):
    k = (H - pad) / ch
    pw, phh = round(cw * k), round(ch * k)
    prod = ph.crop(crop).resize((pw, phh), Image.LANCZOS)
    px, py = round(cx - pw / 2), H - phh
    rows = []
    for y in range(H):
        sy = int(min(max(crop[1] + (y - py) / k, 0), 780))   # wall only, never the podium
        rows.append((A[sy, :25].mean(0) + A[sy, -25:].mean(0)) / 2)
    bg = np.repeat(np.array(rows)[:, None, :], W, 1)
    canvas = Image.fromarray(bg.clip(0, 255).astype(np.uint8))
    m = Image.new("L", prod.size, 255); mp = m.load(); fe = max(14, pw // 8)
    for x in range(pw):
        for y in range(phh):
            v = 255
            if x < fe: v = min(v, 255 * x // fe)
            if pw - 1 - x < fe: v = min(v, 255 * (pw - 1 - x) // fe)
            if y < fe: v = min(v, 255 * y // fe)
            mp[x, y] = v
    canvas.paste(prod, (px, py), m)
    canvas.save(here / f"products/offer2-bg-{name}.jpg", quality=93)

build("1440x300", 1440, 300, cx=880)
build("706x320", 706, 320, cx=530)
build("800x200", 800, 200, cx=560)
