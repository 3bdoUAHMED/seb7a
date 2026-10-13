"""Offer-2 'clean cosmetics' scene (reference: white cubes, cool light backdrop, green leaf sprig).
White matte cubes of varying heights, soft window light + shadows, products grouped on the cubes.
Outputs products/offer2-bg-<W>x<H>-<en|ar>.jpg. RTL mirrors the composition (not the products)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2, math
here = Path(__file__).parent

P = {k: Image.open(here / f"products/{v}.png").convert("RGBA") for k, v in {
    "garlic": "bioxcin-black-garlic-shampoo", "box": "bioxcin-quantum-serum", "forte": "bioxcin-forte-shampoo",
    "serum": "bioxcin-forte-serum", "thermal": "bioxcin-anti-dandruff-shampoo", "pen": "bioxcin-eyelash-serum",
    "qshamp": "bioxcin-quantum-shampoo", "ds": "bioxcin-anti-dandruff-ds-shampoo"}.items()}
REAL_H = {"garlic": 1.0, "box": 0.6, "forte": 0.98, "serum": 0.84, "thermal": 1.08, "pen": 0.92, "qshamp": 1.0, "ds": 0.8}

# one product per cube. Left→right order with row (F = front/low cube, B = back/tall cube)
SEQ = [("garlic", "F"), ("box", "B"), ("forte", "F"), ("serum", "B"),
       ("qshamp", "F"), ("pen", "B"), ("ds", "F"), ("thermal", "B")]
BACK_H = [0.78, 1.0, 0.86, 0.94]     # back cube heights (fraction of hb)
FRONT_H = [0.22, 0.30, 0.18, 0.26]   # front cube heights (fraction of hb)

def backdrop(W, H, rtl):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / W if not rtl else 1 - xx / W
    v = yy / H
    c0, c1 = np.array([236, 240, 243.]), np.array([212, 220, 228.])
    t = np.clip(0.55 * u + 0.45 * v, 0, 1)[..., None]
    img = c0 * (1 - t) + c1 * t
    # soft diagonal window light + shadow bands
    d = (u * W * 0.9 + v * H * 1.6) / max(W, H) * 6.0
    bands = 0.5 + 0.5 * np.sin(d * math.pi)
    bands = cv2.GaussianBlur(bands.astype(np.float32), (0, 0), max(W, H) * 0.02)
    img = img * (0.95 + 0.08 * bands[..., None])
    return img

def leaf_sprig(scale, flip):
    S = 4; Wd, Hd = int(260 * scale * S), int(150 * scale * S)
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def P2(x, y): return (x * S * scale, y * S * scale)
    stem = [(20, 120), (70, 104), (120, 92), (170, 80), (230, 60)]
    d.line([P2(*p) for p in stem], fill=(62, 104, 52, 255), width=int(4 * S * scale))
    leaves = [(55, 108, -150, 62), (88, 98, 30, 70), (125, 90, -140, 72), (160, 82, 40, 66), (200, 70, -130, 60), (232, 60, 10, 52)]
    for (x, y, ang, L) in leaves:
        a = math.radians(ang); pts_l, pts_r = [], []
        for i in range(21):
            t = i / 20; wv = math.sin(math.pi * t) ** 0.85 * L * 0.32
            px, py = x + math.cos(a) * L * t, y + math.sin(a) * L * t
            nx, ny = -math.sin(a), math.cos(a)
            pts_l.append(P2(px + nx * wv, py + ny * wv)); pts_r.append(P2(px - nx * wv, py - ny * wv))
        d.polygon(pts_l + pts_r[::-1], fill=(48, 102, 46, 255))
        d.polygon([P2(x, y)] + pts_l[1:], fill=(72, 132, 62, 255))           # lit half
        d.line([P2(x, y), P2(x + math.cos(a) * L, y + math.sin(a) * L)], fill=(140, 180, 110, 255), width=max(1, int(1.2 * S * scale)))
    im = im.resize((Wd // S, Hd // S), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im

def draw_cube(out, cx, w, h, by, rtl):
    sgn = 1 if not rtl else -1
    w, h = int(w), int(h)
    dx, dy = int(w * 0.10) * sgn, int(w * 0.12)
    xa, xb = int(cx - w / 2), int(cx + w / 2); yt = int(by - h)
    a = np.asarray(out).astype(np.float32).copy()
    xs = np.linspace(0, 1, xb - xa); xs = xs if not rtl else xs[::-1]
    a[yt:int(by), xa:xb] = np.array([246, 247, 248.]) * (1.0 - 0.05 * xs)[None, :, None] * np.linspace(1.0, 0.95, int(by) - yt)[:, None, None]
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(out)
    dr.polygon([(xa, yt), (xb, yt), (xb + dx, yt - dy), (xa + dx, yt - dy)], fill=(253, 253, 253))
    sx = xb if not rtl else xa
    dr.polygon([(sx, yt), (sx + dx, yt - dy), (sx + dx, by - dy), (sx, by)], fill=(222, 226, 231))
    dr.line([(xa, yt), (xb, yt)], fill=(232, 234, 237), width=1)
    return out, (cx + dx / 2, yt - dy * 0.55)

def put_product(out, k, cx, by, h, rtl):
    sgn = 1 if not rtl else -1
    w = P[k].width * h / P[k].height
    e = Image.new("RGBA", (int(w * 1.2), max(4, int(w * 0.16))), (0, 0, 0, 0))
    ImageDraw.Draw(e).ellipse((0, 0, e.width, e.height), fill=(60, 70, 80, 70))
    e = e.filter(ImageFilter.GaussianBlur(max(1.5, w * 0.04)))
    out.paste(e, (int(cx - e.width / 2 + w * 0.12 * sgn), int(by - e.height * 0.5)), e)
    rim = P[k].resize((int(w), int(h)), Image.LANCZOS)
    alpha = rim.getchannel("A").point(lambda v: 0 if v < 24 else v)
    out.paste(rim.convert("RGB"), (int(cx - w / 2), int(by - h)), alpha)
    return out

def cast_shadows(img, cubes, R, rtl):
    H, W = img.shape[:2]; sgn = 1 if not rtl else -1
    sh = np.zeros((H, W), np.float32)
    for cx, w, h, by in cubes:
        off = w * 0.35 * sgn
        pts = np.array([[cx - w / 2, by], [cx + w / 2, by], [cx + w / 2 + off, by - h * 0.95], [cx - w / 2 + off, by - h * 0.95]], np.int32)
        cv2.fillPoly(sh, [pts], 1.0)
    sh = cv2.GaussianBlur(sh, (0, 0), R * 0.02)
    return img * (1 - 0.16 * sh[..., None])

def floor(img, fy):
    H = img.shape[0]
    fl = np.linspace(0, 1, H - fy)[:, None, None]
    img[fy:] = img[fy:] * (1 - 0.6 * (1 - fl * 0.4)) + np.array([246, 247, 248.]) * 0.6 * (1 - fl * 0.4)
    return img

def ratio(k): return P[k].width / P[k].height * REAL_H[k]

def build(W, H, x0, x1, base_back, base_front, hb, u_max, rtl, top_pad=10):
    """Wide: staggered single sequence, back cubes tall, front cubes low."""
    img = floor(backdrop(W, H, rtl), int(base_back - 6))
    R = x1 - x0; gap = 0.07
    # largest u that fits the width and keeps the tallest back product inside the banner
    u_w = R / (sum(ratio(k) * (0.94 if r == "B" else 1) for k, r in SEQ) + gap * (len(SEQ) - 1))
    u_h = min((base_back - hb * BACK_H[i] - top_pad) / (REAL_H[k] * 0.94) for i, (k, r) in enumerate([s for s in SEQ if s[1] == "B"]))
    u = min(u_max, u_w, u_h)
    widths = [ratio(k) * u * (0.94 if r == "B" else 1) for k, r in SEQ]
    total = sum(widths) + gap * u * (len(SEQ) - 1)
    x = x0 + (R - total) / 2
    items, bi, fi = [], 0, 0
    for (k, r), w in zip(SEQ, widths):
        cx = x + w / 2; x += w + gap * u
        if rtl: cx = W - cx
        if r == "B": ch, by, sc = hb * BACK_H[bi], base_back, 0.94; bi += 1
        else: ch, by, sc = hb * FRONT_H[fi], base_front, 1.0; fi += 1
        cw = max(w * 1.35, u * 0.42)
        items.append((r, k, cx, cw, ch, by, sc))
    img = cast_shadows(img, [(cx, cw, ch, by) for r, k, cx, cw, ch, by, sc in items], R, rtl)
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    for r, k, cx, cw, ch, by, sc in sorted(items, key=lambda t: t[0] != "B"):
        out, (tx, ty) = draw_cube(out, cx, cw, ch, by, rtl)
        out = put_product(out, k, tx, ty, u * REAL_H[k] * sc, rtl)
    return out

def build_vertical(W, H, x0, x1, base_front, rtl):
    """Vertical: two packed rows — tall back cubes carry the small items above the front row."""
    img = floor(backdrop(W, H, rtl), int(base_front - 110))
    R = x1 - x0; gap = 0.08
    front = [k for k, r in SEQ if r == "F"]; back = [k for k, r in SEQ if r == "B"]
    uf = R / (sum(ratio(k) for k in front) + gap * 3)
    fh = 110
    front_top = base_front - fh - uf * max(REAL_H[k] for k in front)
    ub = min(R / (sum(ratio(k) for k in back) + gap * 3 + 0.6), uf * 1.05)
    base_back = base_front - 60
    bh = base_back - front_top + uf * 0.25          # back cubes reach a bit above the front products' tops
    cubes = []
    def row(keys, u, by, heights, sc):
        widths = [ratio(k) * u for k in keys]
        tw = sum(widths) + gap * u * (len(keys) - 1)
        x = x0 + (R - tw) / 2; res = []
        for k, w, h in zip(keys, widths, heights):
            cx = x + w / 2; x += w + gap * u
            if rtl: cx = W - cx
            res.append((k, cx, max(w * 1.3, u * 0.45), h, by, u * REAL_H[k] * sc))
        return res
    back_items = row(back, ub, base_back, [bh * f for f in (0.96, 1.0, 0.98, 0.94)], 1.0)
    front_items = row(front, uf, base_front, [fh * f for f in (1.0, 0.82, 0.92, 0.76)], 1.0)
    img = cast_shadows(img, [(cx, cw, ch, by) for k, cx, cw, ch, by, ph in back_items + front_items], R, rtl)
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    for k, cx, cw, ch, by, ph in back_items + front_items:
        out, (tx, ty) = draw_cube(out, cx, cw, ch, by, rtl)
        out = put_product(out, k, tx, ty, ph, rtl)
    return out

SIZES = {  # W, H, x0, x1, base_back, base_front, hb, u_max
    "1440x300": (1440, 300, 560, 1415, 262, 292, 120, 175),
    "706x320": (706, 320, 250, 700, 280, 312, 120, 140),
    "800x200": (800, 200, 300, 794, 176, 196, 80, 110),
}
if False:
    for name, (W, H, x0, x1, bb, bf, hb, um) in SIZES.items():
        for rtl in (False, True):
            build(W, H, x0, x1, bb, bf, hb, um, rtl).save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)
    for rtl in (False, True):
        build_vertical(800, 1200, 30, 770, 1160, rtl).save(here / f"products/offer2-bg-800x1200-{'ar' if rtl else 'en'}.jpg", quality=93)


# ---------- reference 2: two wide white steps, cool backdrop with strong diagonal light ----------
def backdrop2(W, H, rtl):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / W if not rtl else 1 - xx / W
    base = np.array([214, 223, 236.]) * (1 - 0.06 * (yy / H))[..., None]
    # diagonal light shafts (bright) separated by soft shadow bands
    d = (u * W - yy * 0.9) / max(W, H * 2.2)
    shafts = np.zeros_like(d)
    for c, wdt, amp in [(0.18, 0.05, 1.0), (0.34, 0.035, 0.8), (0.55, 0.06, 0.9), (0.78, 0.04, 0.7)]:
        shafts += amp * np.exp(-((d - c) / wdt) ** 2)
    shafts = cv2.GaussianBlur(shafts.astype(np.float32), (0, 0), max(W, H) * 0.006)
    return base * (0.9 + 0.16 * shafts[..., None])

def step(a, xa, xb, yt, yb, depth, rtl, shade=1.0):
    """White block: lit top face (perspective) + front face with light falloff."""
    xa, xb, yt, yb = int(xa), int(xb), int(yt), int(yb)
    xs = np.linspace(0, 1, xb - xa); xs = xs if not rtl else xs[::-1]
    a[yt:yb, xa:xb] = np.array([238, 242, 247.]) * shade * (1.0 - 0.07 * xs)[None, :, None] * np.linspace(1.0, 0.9, yb - yt)[:, None, None]
    a[yt - depth:yt, xa:xb] = np.array([250, 251, 253.]) * np.linspace(0.97, 1.0, depth)[:, None, None]
    a[yt, xa:xb] = [226, 231, 238]
    return a

def build2(W, H, x0, x1, rtl, u, back, front, place):
    """back/front = (x-fraction start, x-fraction end, top y, bottom y). place = list of (key, 'B'|'F', x-fraction)."""
    a = backdrop2(W, H, rtl)
    R = x1 - x0
    def X(f): return x0 + f * R if not rtl else W - (x0 + f * R)
    depth_b, depth_f = max(8, int(H * 0.05)), max(8, int(H * 0.06))
    # block shadows on the wall (light from upper left)
    sgn = 1 if not rtl else -1
    sh = np.zeros(a.shape[:2], np.float32)
    for (fa, fb, yt, yb) in (back, front):
        xa, xb = sorted((X(fa), X(fb)))
        cv2.rectangle(sh, (int(xa + R * 0.05 * sgn), int(yt - H * 0.05)), (int(xb + R * 0.05 * sgn), int(yb)), 1.0, -1)
    a = a * (1 - 0.14 * cv2.GaussianBlur(sh, (0, 0), R * 0.02)[..., None])
    for blk, dep, shd in ((back, depth_b, 0.98), (front, depth_f, 1.0)):
        fa, fb, yt, yb = blk; xa, xb = sorted((X(fa), X(fb)))
        a = step(a, xa, xb, yt, yb, dep, rtl, shd)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    for row in ("B", "F"):
        blk, dep = (back, depth_b) if row == "B" else (front, depth_f)
        by = blk[2] - dep * 0.45
        for k, r, f in place:
            if r != row: continue
            out = put_product(out, k, X(f), by, u * REAL_H[k], rtl)
    return out

LAYOUT2 = {  # W, H, x0, x1, u, back, front, place
    "1440x300": (1440, 300, 620, 1410, 150, (0.0, 0.60, 200, 300), (0.50, 1.0, 250, 300), [("forte", "B", 0.07), ("garlic", "B", 0.2), ("thermal", "B", 0.32), ("qshamp", "B", 0.445),
                  ("serum", "F", 0.58), ("box", "F", 0.72), ("pen", "F", 0.855), ("ds", "F", 0.95)]),
    "706x320": (706, 320, 290, 700, 118, (0.0, 0.60, 214, 320), (0.50, 1.0, 266, 320), [("forte", "B", 0.07), ("garlic", "B", 0.2), ("thermal", "B", 0.32), ("qshamp", "B", 0.445),
                  ("serum", "F", 0.58), ("box", "F", 0.72), ("pen", "F", 0.855), ("ds", "F", 0.95)]),
    "800x200": (800, 200, 370, 796, 82, (0.0, 0.60, 136, 200), (0.50, 1.0, 168, 200), [("forte", "B", 0.07), ("garlic", "B", 0.2), ("thermal", "B", 0.32), ("qshamp", "B", 0.445),
                  ("serum", "F", 0.58), ("box", "F", 0.72), ("pen", "F", 0.855), ("ds", "F", 0.95)]),
    "800x1200": (800, 1200, 40, 760, 225, (0.0, 0.62, 860, 1200), (0.38, 1.0, 1070, 1200),
                 [("forte", "B", 0.08), ("garlic", "B", 0.25), ("thermal", "B", 0.4), ("qshamp", "B", 0.555),
                  ("serum", "F", 0.48), ("box", "F", 0.665), ("pen", "F", 0.83), ("ds", "F", 0.935)]),
}
if __name__ == "__main__":
    for name, (W, H, x0, x1, u, back, front, place) in LAYOUT2.items():
        for rtl in (False, True):
            build2(W, H, x0, x1, rtl, u, back, front, place).save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)
