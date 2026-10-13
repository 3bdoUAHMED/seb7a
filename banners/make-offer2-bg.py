"""Offer-2 wide backgrounds (built per size and per direction).
Three travertine plinths (tall centre, low left, mid right) with the 8 products grouped on them,
on a wall extended from the podium photo's tones. RTL mirrors the composition (not the products)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2
here = Path(__file__).parent
ph = Image.open(here / "products/offer2-podium.jpg").convert("RGB")
A = np.asarray(ph).astype(np.float32)
rng = np.random.default_rng(11)

def travertine(w, h, shade=1.0, k=1.0):
    w, h = max(1, int(w)), max(1, int(h))
    base = np.array([230, 219, 203], np.float32)
    n1 = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 10 * k + 1)
    n1 = n1 / (n1.std() + 1e-6) * 3.2
    pores = np.zeros((h, w), np.float32)
    for _ in range(int(w * h / (110 / k))):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        rx = max(1, int(rng.choice([1, 1, 1, 2, 2, 3]) * k + .5)); ry = max(1, int(rx * .5))
        cv2.ellipse(pores, (x, y), (rx, ry), 0, 0, 360, float(rng.uniform(6, 14)), -1)
    pores = cv2.GaussianBlur(pores, (0, 0), .7)
    img = base + n1[..., None] - pores[..., None] * np.array([1.0, 1.1, 1.3])
    img *= shade
    return img

def wall(W, H):
    rows = [(A[int(110 + y / max(1, H - 1) * 620), :25].mean(0) + A[int(110 + y / max(1, H - 1) * 620), -25:].mean(0)) / 2 for y in range(H)]
    bg = np.repeat(np.array(rows)[:, None, :], W, 1)
    return bg

P = {k: Image.open(here / f"products/{v}.png").convert("RGBA") for k, v in {
    "garlic": "bioxcin-black-garlic-shampoo", "box": "bioxcin-quantum-serum", "forte": "bioxcin-forte-shampoo",
    "serum": "bioxcin-forte-serum", "thermal": "bioxcin-anti-dandruff-shampoo", "pen": "bioxcin-eyelash-serum",
    "qshamp": "bioxcin-quantum-shampoo", "ds": "bioxcin-anti-dandruff-ds-shampoo"}.items()}
REAL_H = {"garlic": 1.0, "box": 0.6, "forte": 0.98, "serum": 0.84, "thermal": 1.08, "pen": 0.92, "qshamp": 1.0, "ds": 0.8}

# plinths as fractions of the stage width; products: (key, plinth, x-fraction of stage)
PLINTHS = {"C": (0.25, 0.75), "L": (0.0, 0.35), "R": (0.65, 1.0)}
PRODUCTS = [("box", "C", 0.405), ("serum", "C", 0.505), ("pen", "C", 0.565), ("thermal", "C", 0.63),
            ("garlic", "L", 0.095), ("forte", "L", 0.255), ("qshamp", "R", 0.765), ("ds", "R", 0.915)]

def build(name, W, H, x0, x1, u, hl, hr, hc, rtl, tex=1.0):
    img = wall(W, H)
    R = x1 - x0
    u = min(u, 0.27 * R)
    def X(f):  # stage fraction -> pixel x (mirrored for RTL)
        return x0 + f * R if not rtl else W - (x0 + f * R)
    heights = {"L": hl, "R": hr, "C": hc}
    top_d = max(8, int(R * 0.03))            # visible depth of the top face
    # cast shadow of plinths on the wall (light from the upper left / right in RTL)
    sh = np.zeros((H, W), np.float32)
    for key, (a, b) in PLINTHS.items():
        xa, xb = sorted((X(a), X(b)))
        off = R * 0.05 * (1 if not rtl else -1)
        cv2.rectangle(sh, (int(xa + off), int(H - heights[key] - top_d)), (int(xb + off), H), 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), R * 0.03)
    img = img * (1 - 0.22 * sh[..., None])
    def plinth(key):
        nonlocal img
        a, b = PLINTHS[key]; xa, xb = sorted((int(X(a)), int(X(b)))); h = int(heights[key])
        w = xb - xa
        front = travertine(w, h, 1.0, tex)
        front *= np.linspace(1.02, 0.9, h)[:, None, None]
        # soft ambient occlusion on the edges of the front face
        edge = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)
        front *= (0.9 + 0.1 * np.clip(edge / (w * 0.08), 0, 1))[None, :, None]
        top = travertine(w, top_d, 1.08, tex)
        top *= np.linspace(1.04, 0.98, top_d)[:, None, None]
        img[H - h:H, xa:xb] = front
        img[H - h - top_d:H - h, xa:xb] = top
        img[H - h - top_d, xa:xb] = [248, 243, 235]          # crisp front edge highlight
        img[H - h, xa:xb] *= 0.93
    # centre plinth first (behind), then the two front plinths
    plinth("C")
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    def put(key, pl):
        h = u * REAL_H[key] * (0.82 if pl == "C" else 1.0)
        im = P[key]; w = im.width * h / im.height
        cx = X([p for p in PRODUCTS if p[0] == key][0][2])
        base_y = H - heights[pl] - top_d * 0.45
        e = Image.new("RGBA", (int(w * 1.1), max(6, int(u * .08))), (0, 0, 0, 0))
        ImageDraw.Draw(e).ellipse((0, 0, e.width, e.height), fill=(80, 60, 40, 110))
        e = e.filter(ImageFilter.GaussianBlur(max(2, u * .025)))
        out.paste(e, (int(cx - w * .55 + (u * .03 if not rtl else -u * .03)), int(base_y - e.height * .55)), e)
        r = im.resize((int(w), int(h)), Image.LANCZOS)
        out.paste(r, (int(cx - w / 2), int(base_y - h)), r)
    for key, pl, _ in PRODUCTS:
        if pl == "C": put(key, pl)
    img = np.asarray(out).astype(np.float32)
    plinth("L"); plinth("R")
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    for key, pl, _ in PRODUCTS:
        if pl != "C": put(key, pl)
    out.save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)

for rtl in (False, True):
    build("1440x300", 1440, 300, 700, 1400, u=158, hl=30, hr=46, hc=104, rtl=rtl, tex=0.8)
    build("706x320", 706, 320, 318, 700, u=150, hl=28, hr=42, hc=104, rtl=rtl, tex=0.7)
    build("800x200", 800, 200, 400, 790, u=104, hl=14, hr=24, hc=64, rtl=rtl, tex=0.55)
