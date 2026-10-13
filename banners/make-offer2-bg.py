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
# cylinder pedestals: name -> (x-fraction, width-fraction of stage, height-fraction of hmax, front offset px-fraction)
PEDS = {"C": (0.52, 0.26, 0.66, 0.0), "B": (0.30, 0.17, 0.42, 0.0), "D": (0.755, 0.20, 0.46, 0.0),
        "A": (0.10, 0.20, 0.20, 0.0), "E": (0.925, 0.15, 0.26, 0.0)}
ON = {"C": ["box", "pen"], "B": ["forte"], "D": ["serum", "thermal"], "A": ["garlic", "ds"], "E": ["qshamp"]}
DRAW = ["C", "B", "D", "A", "E"]                # back to front

def leaf_shadow(W, H, x, y, s, rtl):
    m = np.zeros((H, W), np.float32)
    for i in range(9):
        ang = -60 + i * 15
        L = s * (0.55 + 0.05 * (4 - abs(i - 4)))
        cx = x + np.cos(np.radians(ang)) * L * 0.5 * (1 if not rtl else -1)
        cy = y + np.sin(np.radians(ang)) * L * 0.5
        cv2.ellipse(m, (int(cx), int(cy)), (int(L * 0.5), int(s * 0.06)), ang if not rtl else 180 - ang, 0, 360, 1.0, -1)
    cv2.line(m, (int(x), int(y)), (int(x + (s * 0.9 if not rtl else -s * 0.9)), int(y - s * 0.6)), 1.0, max(2, int(s * 0.012)))
    return cv2.GaussianBlur(m, (0, 0), s * 0.03)

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

def build(name, W, H, x0, x1, floor_h, u, hmax, rtl):
    a = scene(W, H, floor_h)
    R = x1 - x0
    def X(f): return x0 + f * R if not rtl else W - (x0 + f * R)
    fy = H - floor_h
    base_back = fy + floor_h * 0.45
    base_front = fy + floor_h * 0.9
    # soft palm-leaf shadow on the wall above the products
    ls = leaf_shadow(W, H, X(0.92), H * 0.05, H * 0.9, rtl)
    a = a * (1 - 0.10 * ls[..., None])
    # shadows of pedestals on wall/floor
    sh = np.zeros((H, W), np.float32)
    for k, (f, wf, hf, fr) in PEDS.items():
        w = wf * R; h = hf * hmax; by = base_front if fr else base_back
        cv2.rectangle(sh, (int(X(f) - w / 2), int(by - h)), (int(X(f) + w / 2), int(by)), 1.0, -1)
        cv2.ellipse(sh, (int(X(f) + (w * .12 if not rtl else -w * .12)), int(by)), (int(w * .62), int(w * .09)), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), R * 0.02)
    sh = np.roll(sh, int(R * 0.02) * (1 if not rtl else -1), axis=1)
    a = a * (1 - 0.2 * sh[..., None])
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))

    def cylinder(k):
        nonlocal img
        f, wf, hf, fr = PEDS[k]
        w = int(wf * R); h = int(hf * hmax); by = int(base_front if fr else base_back)
        eh = max(4, int(w * 0.16))                       # ellipse height (top/bottom caps)
        cx = X(f); xa = int(cx - w / 2)
        arr = np.asarray(img).astype(np.float32).copy()
        tex = travertine(w, h + eh, 1.0)
        # cylindrical shading: light from the upper left (right in RTL)
        xs = np.linspace(-1, 1, w)
        if rtl: xs = -xs
        shade = 0.84 + 0.2 * np.cos(np.clip((xs + 0.35) * 1.3, -np.pi / 2, np.pi / 2))
        body = tex * shade[None, :, None]
        yy, xx = np.mgrid[0:h + eh, 0:w]
        # body mask = rect from top-cap centre to bottom-cap centre + bottom half ellipse
        ex = (xx - w / 2) / (w / 2)
        bottom = (yy <= (h + eh / 2) + (eh / 2) * np.sqrt(np.clip(1 - ex ** 2, 0, 1)))
        topcap = (yy >= eh / 2 - (eh / 2) * np.sqrt(np.clip(1 - ex ** 2, 0, 1)))
        mask = bottom & topcap
        y0 = by - h - eh // 2
        region = arr[y0:y0 + h + eh, xa:xa + w]
        mm = mask[:region.shape[0], :region.shape[1]]
        region[mm] = body[:region.shape[0], :region.shape[1]][mm]
        # top cap (lighter ellipse) + rim highlight
        cap = travertine(w, eh, 1.09)
        capmask = ((xx[:eh] - w / 2) / (w / 2)) ** 2 + ((yy[:eh] - eh / 2) / (eh / 2)) ** 2 <= 1
        cr = arr[y0:y0 + eh, xa:xa + w]
        cm = capmask[:cr.shape[0], :cr.shape[1]]
        cr[cm] = cap[:cr.shape[0], :cr.shape[1]][cm]
        img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        d.ellipse((xa, y0, xa + w - 1, y0 + eh - 1), outline=(250, 246, 240), width=1)
        return by - h, w, eh

    tops = {}
    for k in DRAW:
        top_y, w, eh = cylinder(k)
        tops[k] = (top_y, w, eh)
        # products standing on this pedestal
        keys = ON[k]; f = PEDS[k][0]
        hs = [u * REAL_H[q] * (0.9 if PEDS[k][3] == 0 else 1.0) for q in keys]
        ws = [P[q].width * hh / P[q].height for q, hh in zip(keys, hs)]
        kf = min(1.0, (w * 0.9) / (sum(ws) + u * 0.04 * (len(keys) - 1)))
        hs = [hh * kf for hh in hs]; ws = [ww * kf for ww in ws]
        total = sum(ws) + u * 0.04 * kf * (len(keys) - 1)
        rel = -total / 2
        for q, hh, ww in zip(keys, hs, ws):
            c = X(f) + (rel + ww / 2) * (1 if not rtl else -1); rel += ww + u * 0.04 * kf
            by = top_y + eh * 0.05
            e = Image.new("RGBA", (int(ww * 1.1), max(4, int(eh * 0.6))), (0, 0, 0, 0))
            ImageDraw.Draw(e).ellipse((0, 0, e.width, e.height), fill=(90, 70, 45, 110))
            e = e.filter(ImageFilter.GaussianBlur(max(1.5, eh * 0.12)))
            img.paste(e, (int(c - e.width / 2), int(by - e.height * 0.5)), e)
            rim = P[q].resize((int(ww), int(hh)), Image.LANCZOS)
            alpha = rim.getchannel("A").point(lambda v: 0 if v < 24 else v)
            img.paste(rim.convert("RGB"), (int(c - ww / 2), int(by - hh)), alpha)
    img.save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)

for rtl in (False, True):
    build("1440x300", 1440, 300, 690, 1410, floor_h=46, u=136, hmax=150, rtl=rtl)
    build("706x320", 706, 320, 314, 702, floor_h=44, u=112, hmax=150, rtl=rtl)
    build("800x200", 800, 200, 396, 794, floor_h=28, u=88, hmax=96, rtl=rtl)
