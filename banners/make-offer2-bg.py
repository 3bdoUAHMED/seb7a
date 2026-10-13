"""Offer-2 wide backgrounds: the real wall of the podium photo, a soft light floor,
and the 8 products standing on the floor in two loose rows (no stands). RTL mirrors the layout."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2
here = Path(__file__).parent
ph = Image.open(here / "products/offer2-podium.jpg").convert("RGB")

P = {k: Image.open(here / f"products/{v}.png").convert("RGBA") for k, v in {
    "garlic": "bioxcin-black-garlic-shampoo", "box": "bioxcin-quantum-serum", "forte": "bioxcin-forte-shampoo",
    "serum": "bioxcin-forte-serum", "thermal": "bioxcin-anti-dandruff-shampoo", "pen": "bioxcin-eyelash-serum",
    "qshamp": "bioxcin-quantum-shampoo", "ds": "bioxcin-anti-dandruff-ds-shampoo"}.items()}
REAL_H = {"garlic": 1.0, "box": 0.6, "forte": 0.98, "serum": 0.84, "thermal": 1.08, "pen": 0.92, "qshamp": 1.0, "ds": 0.8}
# one row on the floor; odd items stand a little further back (higher, slightly smaller)
ORDER = ["serum", "garlic", "pen", "forte", "box", "qshamp", "thermal", "ds"]

def scene(W, H, floor_h):
    # wall: clean upper part of the photo (soft light + panel shadows), scaled to the banner
    wall = ph.crop((0, 40, 800, 420)).resize((W, H), Image.LANCZOS)
    a = np.asarray(wall).astype(np.float32)
    # floor: light stone tone from the photo's floor, with a soft horizon
    fy = H - floor_h
    floor_top, floor_bot = np.array([238, 234, 228.]), np.array([226, 221, 215.])
    t = np.linspace(0, 1, floor_h)[:, None, None]
    a[fy:] = floor_top * (1 - t) + floor_bot * t
    blend = 10
    for i in range(blend):
        k = i / blend
        a[fy - blend + i] = a[fy - blend + i] * (1 - k) + floor_top * k
    a[fy - 1:fy + 2] *= 0.985
    return a

def build(name, W, H, x0, x1, floor_h, rtl):
    a = scene(W, H, floor_h)
    fy = H - floor_h
    R = x1 - x0
    # size so the whole row fits the product area (with a slight overlap)
    widths = [P[k].width / P[k].height * REAL_H[k] for k in ORDER]
    gap = -0.03
    u = min((H - floor_h * 0.2) * 0.86, R / (sum(widths) + gap * (len(ORDER) - 1)))
    total = u * (sum(widths) + gap * (len(ORDER) - 1))
    x = x0 + (R - total) / 2
    items = []
    for i, k in enumerate(ORDER):
        back = i % 2 == 1
        sc = 0.94 if back else 1.0
        h = u * REAL_H[k] * sc; w = P[k].width * h / P[k].height
        cx = x + u * widths[i] / 2
        x += u * (widths[i] + gap)
        if rtl: cx = W - cx
        base = fy + floor_h * (0.42 if back else 0.72)
        items.append((back, k, cx, base, w, h))
    # contact shadows (drawn into the floor before any product)
    sh = np.zeros((H, W), np.float32)
    for back, k, cx, base, w, h in items:
        off = u * 0.05 * (1 if not rtl else -1)
        cv2.ellipse(sh, (int(cx + off), int(base)), (int(w * 0.6), max(3, int(u * 0.045))), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), max(2, u * 0.03))
    a = a * (1 - 0.32 * sh[..., None])
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    for back, k, cx, base, w, h in sorted(items, key=lambda t: not t[0]):   # back row first
        rim = P[k].resize((int(w), int(h)), Image.LANCZOS)
        alpha = rim.getchannel("A").point(lambda v: 0 if v < 24 else v)   # drop faint fringe
        img.paste(rim.convert("RGB"), (int(cx - w / 2), int(base - h)), alpha)
    img.save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)

for rtl in (False, True):
    build("1440x300", 1440, 300, 690, 1410, floor_h=58, rtl=rtl)
    build("706x320", 706, 320, 318, 700, floor_h=60, rtl=rtl)
    build("800x200", 800, 200, 400, 792, floor_h=40, rtl=rtl)
