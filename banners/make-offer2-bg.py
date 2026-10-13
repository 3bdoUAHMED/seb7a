"""Offer-2 wide backgrounds: wall from the podium photo's tones, stone blocks built from
the photo's travertine texture, and the 8 product cutouts arranged per banner size."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
here = Path(__file__).parent
ph = Image.open(here / "products/offer2-podium.jpg").convert("RGB")
A = np.asarray(ph).astype(np.float32)

# travertine: warm base + soft cloudy variation + small elongated pores (like the photo's blocks)
import cv2
rng = np.random.default_rng(7)
def travertine(w, h, shade=1.0, scale=1.0):
    base = np.array([229, 217, 200], np.float32)
    n1 = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 9 * scale + 1)
    n1 = n1 / (n1.std() + 1e-6) * 4.0
    n2 = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.8) * 3.0
    pores = np.zeros((h, w), np.float32)
    for _ in range(int(w * h / (80 / scale))):
        x, y = rng.integers(0, w), rng.integers(0, h)
        rx = max(1, int(rng.choice([1, 1, 2, 2, 3]) * scale + 0.5)); ry = max(1, int(rx * 0.55))
        cv2.ellipse(pores, (int(x), int(y)), (rx, ry), 0, 0, 360, float(rng.uniform(7, 17)), -1)
    pores = cv2.GaussianBlur(pores, (0, 0), 0.6)
    img = base[None, None, :] + (n1 + n2)[..., None] - pores[..., None] * np.array([1.0, 1.08, 1.25])
    img *= shade * np.linspace(1.02, 0.95, h)[:, None, None]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))

def stone(w, h, shade=1.0, scale=1.0):
    return travertine(max(1, int(w)), max(1, int(h)), shade, scale)

def wall(W, H):
    rows = []
    for y in range(H):
        sy = int(120 + (y / max(1, H - 1)) * 640)
        rows.append((A[sy, :25].mean(0) + A[sy, -25:].mean(0)) / 2)
    bg = np.repeat(np.array(rows)[:, None, :], W, 1)
    xx = np.linspace(-1, 1, W)[None, :, None]
    bg = bg * (1 - 0.05 * xx ** 2)             # soft light in the middle
    return Image.fromarray(bg.clip(0, 255).astype(np.uint8))

P = {k: Image.open(here / f"products/{v}.png").convert("RGBA") for k, v in {
    "garlic": "bioxcin-black-garlic-shampoo", "box": "bioxcin-quantum-serum", "forte": "bioxcin-forte-shampoo",
    "serum": "bioxcin-forte-serum", "thermal": "bioxcin-anti-dandruff-shampoo", "pen": "bioxcin-eyelash-serum",
    "qshamp": "bioxcin-quantum-shampoo", "ds": "bioxcin-anti-dandruff-ds-shampoo"}.items()}
REAL_H = {"garlic": 1.0, "box": 0.62, "forte": 0.98, "serum": 0.86, "thermal": 1.06, "pen": 0.95, "qshamp": 1.0, "ds": 0.82}
# slot order left→right: front (F) shampoos on low blocks, back (B) small items on tall blocks
SLOTS = [("garlic", "F"), ("box", "B"), ("forte", "F"), ("serum", "B"),
         ("qshamp", "F"), ("pen", "B"), ("ds", "F"), ("thermal", "B")]
BACK_H = [0.84, 1.0, 0.9, 0.74]
FRONT_H = [0.14, 0.24, 0.1, 0.2]

def build(name, W, H, x0, x1, unit, maxblock, slab, tex, front_h=0.16):
    from PIL import ImageDraw
    c = wall(W, H)
    ground = H - slab
    n = len(SLOTS)
    step = (x1 - x0) / n
    items = []
    bi = 0; fi = 0
    for i, (k, row) in enumerate(SLOTS):
        im = P[k]
        h = unit * REAL_H[k] * (0.9 if row == "B" else 0.78)
        w = im.width * h / im.height
        cx = x0 + step * (i + 0.5)
        if row == "B":
            bh = int(maxblock * BACK_H[bi]); bi += 1
            bw = max(w * 1.3, step * 1.2)
        else:
            bh = int(maxblock * FRONT_H[fi]); fi += 1
            bw = max(w * 1.15, step * 1.1)
        items.append(dict(k=k, row=row, cx=cx, w=w, h=h, bh=bh, bw=bw))
    top_h = max(5, int(unit * 0.07))
    # soft shadows of the blocks on the wall (light from the upper left)
    shadow = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(shadow)
    for it in items:
        if it["row"] == "B":
            sd.rectangle((it["cx"] - it["bw"] / 2 + unit * 0.12, ground - it["bh"] - top_h,
                          it["cx"] + it["bw"] / 2 + unit * 0.12, ground), fill=55)
    shadow = shadow.filter(ImageFilter.GaussianBlur(unit * 0.12))
    c = Image.composite(Image.new("RGB", (W, H), (150, 128, 104)), c, shadow)
    # base slab
    bx0 = int(x0 - unit * 0.15)
    c.paste(stone(int(x1 - x0 + unit * 0.3), slab, 0.96, tex), (bx0, ground))
    c.paste(stone(int(x1 - x0 + unit * 0.3), 3, 1.1, tex), (bx0, ground - 2))

    def draw_block(it):
        x = int(it["cx"] - it["bw"] / 2); bw = int(it["bw"]); bh = it["bh"]
        if bh <= 0: return
        side = max(3, int(bw * 0.07))
        c.paste(stone(bw, bh, 1.0, tex), (x, ground - bh))
        c.paste(stone(side, bh + top_h, 0.86, tex), (x + bw, ground - bh - top_h))     # shaded right side
        c.paste(stone(bw + side, top_h, 1.1, tex), (x, ground - bh - top_h))           # lit top
        d = ImageDraw.Draw(c)
        d.line((x, ground - bh - top_h, x + bw + side, ground - bh - top_h), fill=(247, 241, 232), width=1)
        d.line((x, ground - bh, x + bw, ground - bh), fill=(208, 194, 175), width=1)
        sh = Image.new("L", (bw + side, 7), 0); ImageDraw.Draw(sh).rectangle((0, 0, bw + side, 7), fill=45)
        c.paste((120, 100, 80), (x, ground - 7), sh.filter(ImageFilter.GaussianBlur(2)))

    def draw_product(it):
        im = P[it["k"]].resize((int(it["w"]), int(it["h"])), Image.LANCZOS)
        px, py = int(it["cx"] - it["w"] / 2), int(ground - it["bh"] - top_h * 0.5 - it["h"])
        e = Image.new("RGBA", (int(it["w"] * 1.4), max(6, int(unit * 0.1))), (0, 0, 0, 0))
        ImageDraw.Draw(e).ellipse((0, 0, e.width, e.height), fill=(70, 50, 30, 120))
        e = e.filter(ImageFilter.GaussianBlur(max(2, unit * 0.025)))
        c.paste(e, (int(px - it["w"] * 0.2 + unit * 0.04), int(py + it["h"] - e.height * 0.6)), e)
        c.paste(im, (px, py), im)

    back = [it for it in items if it["row"] == "B"]
    front = [it for it in items if it["row"] == "F"]
    for it in sorted(back, key=lambda t: -t["bh"]): draw_block(it)
    for it in back: draw_product(it)
    for it in front: draw_block(it)
    for it in front: draw_product(it)
    c.save(here / f"products/offer2-bg-{name}.jpg", quality=93)

build("1440x300", 1440, 300, 700, 1390, unit=160, maxblock=128, slab=22, tex=0.7)
build("706x320", 706, 320, 362, 702, unit=150, maxblock=140, slab=20, tex=0.6)
build("800x200", 800, 200, 430, 790, unit=104, maxblock=86, slab=14, tex=0.5)
