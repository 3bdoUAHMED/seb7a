"""Offer-2 wide backgrounds: the real wall of the podium photo, a soft light floor,
and the 8 products standing on the floor in two loose rows (no stands). RTL mirrors the layout."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2
rng = np.random.default_rng(5)

def travertine(w, h, shade=1.0):
    w, h = max(1, int(w)), max(1, int(h))
    base = np.array([233, 224, 210], np.float32)
    n1 = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 12)
    n1 = n1 / (n1.std() + 1e-6) * 2.4
    pores = np.zeros((h, w), np.float32)
    for _ in range(int(w * h / 160)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        rx = int(rng.choice([1, 1, 1, 2])); cv2.ellipse(pores, (x, y), (rx, max(1, rx // 2)), 0, 0, 360, float(rng.uniform(5, 11)), -1)
    pores = cv2.GaussianBlur(pores, (0, 0), .6)
    return (base + n1[..., None] - pores[..., None] * np.array([1, 1.1, 1.3])) * shade
here = Path(__file__).parent
ph = Image.open(here / "products/offer2-podium.jpg").convert("RGB")

P = {k: Image.open(here / f"products/{v}.png").convert("RGBA") for k, v in {
    "garlic": "bioxcin-black-garlic-shampoo", "box": "bioxcin-quantum-serum", "forte": "bioxcin-forte-shampoo",
    "serum": "bioxcin-forte-serum", "thermal": "bioxcin-anti-dandruff-shampoo", "pen": "bioxcin-eyelash-serum",
    "qshamp": "bioxcin-quantum-shampoo", "ds": "bioxcin-anti-dandruff-ds-shampoo"}.items()}
REAL_H = {"garlic": 1.0, "box": 0.6, "forte": 0.98, "serum": 0.84, "thermal": 1.08, "pen": 0.92, "qshamp": 1.0, "ds": 0.8}
# 3-tier steps: (key, tier, x-fraction of the stage). Tier 0 = bottom step (front, biggest products).
TIERS = [1.0, 0.64, 0.32]                      # step widths as a fraction of the stage
# products per visible tread segment: (tier, side) -> keys (side: L, R, or C for the top step)
GROUPS = {(2, "C"): ["serum", "box", "pen"],
          (1, "L"): ["forte"], (1, "R"): ["thermal", "ds"],
          (0, "L"): ["garlic"], (0, "R"): ["qshamp"]}

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

def build(name, W, H, x0, x1, floor_h, u, th, rtl):
    a = scene(W, H, floor_h)
    R = x1 - x0
    cx0 = x0 + R / 2 if not rtl else W - (x0 + R / 2)
    base_y = H - int(floor_h * 0.3)                  # where the bottom step meets the floor
    depth = max(6, int(th * 0.22))                   # visible depth of each tread
    # soft shadow of the whole stack on the wall / floor
    sh = np.zeros((H, W), np.float32)
    for t, f in enumerate(TIERS):
        hw = R * f / 2; top = base_y - th * (t + 1) - depth
        cv2.rectangle(sh, (int(cx0 - hw), int(top)), (int(cx0 + hw), base_y), 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), R * 0.035)
    off = int(R * 0.025) * (1 if not rtl else -1)
    sh = np.roll(sh, off, axis=1)
    a = a * (1 - 0.18 * sh[..., None])
    def tread_y(t): return base_y - th * (t + 1)
    for t, f in enumerate(TIERS):                     # draw bottom step first, then the ones above
        hw = int(R * f / 2); xa, xb = int(cx0 - hw), int(cx0 + hw)
        y0 = tread_y(t)
        front = travertine(xb - xa, th, 1.0) * np.linspace(1.0, 0.9, th)[:, None, None]
        edge = np.minimum(np.arange(xb - xa), np.arange(xb - xa)[::-1]).astype(np.float32)
        front *= (0.93 + 0.07 * np.clip(edge / 10, 0, 1))[None, :, None]
        a[y0:y0 + th, xa:xb] = front
        top = travertine(xb - xa, depth, 1.07) * np.linspace(1.03, 0.99, depth)[:, None, None]
        a[y0 - depth:y0, xa:xb] = top
        a[y0 - depth, xa:xb] = [250, 246, 239]
        a[y0, xa:xb] *= 0.9                           # crisp edge between tread and riser
        if t > 0:                                     # contact shade where this step sits on the one below
            a[y0 + th - 3:y0 + th, xa:xb] *= 0.88
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    # products: top step first (furthest back), bottom step last (in front)
    def seg(t, side):
        hw = R * TIERS[t] / 2
        if side == "C": return (-hw, hw)
        inner = R * TIERS[t + 1] / 2
        return (-hw, -inner) if side == "L" else (inner, hw)
    for t in (2, 1, 0):
        sc = (1.0, 0.94, 0.88)[t]
        for (tier, side), keys in GROUPS.items():
            if tier != t: continue
            a0, a1 = seg(t, side); L = (a1 - a0) * 0.92
            hs = [u * REAL_H[k] * sc for k in keys]
            ws = [P[k].width * h / P[k].height for k, h in zip(keys, hs)]
            gap = u * 0.05
            k_fit = min(1.0, L / (sum(ws) + gap * (len(keys) - 1)))
            hs = [h * k_fit for h in hs]; ws = [w * k_fit for w in ws]
            total = sum(ws) + gap * k_fit * (len(keys) - 1)
            xs = (a0 + a1) / 2 - total / 2
            for k, h, w in zip(keys, hs, ws):
                rel = xs + w / 2; xs += w + gap * k_fit
                cx = cx0 + (rel if not rtl else -rel)
                by = tread_y(t) - depth * 0.45
                e = Image.new("RGBA", (int(w * 1.15), max(5, int(depth * 0.9))), (0, 0, 0, 0))
                ImageDraw.Draw(e).ellipse((0, 0, e.width, e.height), fill=(90, 70, 45, 115))
                e = e.filter(ImageFilter.GaussianBlur(max(1.5, depth * 0.2)))
                img.paste(e, (int(cx - e.width / 2 + (2 if not rtl else -2)), int(by - e.height * 0.55)), e)
                rim = P[k].resize((int(w), int(h)), Image.LANCZOS)
                alpha = rim.getchannel("A").point(lambda v: 0 if v < 24 else v)
                img.paste(rim.convert("RGB"), (int(cx - w / 2), int(by - h)), alpha)
    img.save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)

for rtl in (False, True):
    build("1440x300", 1440, 300, 690, 1410, floor_h=40, u=150, th=50, rtl=rtl)
    build("706x320", 706, 320, 312, 702, floor_h=36, u=122, th=56, rtl=rtl)
    build("800x200", 800, 200, 396, 794, floor_h=22, u=96, th=33, rtl=rtl)
