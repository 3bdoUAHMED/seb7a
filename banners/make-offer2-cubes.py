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

# cubes: name -> (centre x-fraction, width-fraction, height-fraction, row)  row 0 = back, 1 = front
CUBES = {"A": (0.30, 0.25, 0.50, 0), "B": (0.60, 0.27, 0.70, 0), "C": (0.875, 0.23, 0.42, 0),
         "D": (0.11, 0.22, 0.20, 1), "E": (0.73, 0.17, 0.13, 1)}
ON = {"A": ["forte", "serum"], "B": ["box", "pen"], "C": ["qshamp", "thermal"], "D": ["garlic"], "E": ["ds"]}
ORDER = ["B", "A", "C", "D", "E"]

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

def build(W, H, x0, x1, base_back, base_front, hmax, u, rtl, leaf=(0.44, 0.95)):
    img = backdrop(W, H, rtl)
    R = x1 - x0
    def X(f): return x0 + f * R if not rtl else W - (x0 + f * R)
    sgn = 1 if not rtl else -1
    # floor: bright surface under the cubes
    fy = int(base_back - (base_front - base_back) * 0.2)
    fl = np.linspace(0, 1, H - fy)[:, None, None]
    img[fy:] = img[fy:] * (1 - 0.6 * (1 - fl * 0.4)) + np.array([246, 247, 248.]) * 0.6 * (1 - fl * 0.4)
    # cast shadows (light from upper left → shadows to the right; mirrored in RTL)
    sh = np.zeros((H, W), np.float32)
    for k, (f, wf, hf, row) in CUBES.items():
        w, h = wf * R, hf * hmax; by = base_front if row else base_back
        x = X(f); off = w * 0.35 * sgn
        pts = np.array([[x - w / 2, by], [x + w / 2, by], [x + w / 2 + off, by - h * 0.95], [x - w / 2 + off, by - h * 0.95]], np.int32)
        cv2.fillPoly(sh, [pts], 1.0)
    sh = cv2.GaussianBlur(sh, (0, 0), R * 0.022)
    img = img * (1 - 0.16 * sh[..., None])
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))

    def cube(k):
        nonlocal out
        f, wf, hf, row = CUBES[k]
        w, h = int(wf * R), int(hf * hmax); by = int(base_front if row else base_back)
        dx, dy = int(w * 0.10) * sgn, int(w * 0.13)
        cx = X(f); xa, xb = int(cx - w / 2), int(cx + w / 2); yt = by - h
        a = np.asarray(out).astype(np.float32).copy()
        # front face: matte white with gentle vertical falloff + slight horizontal light
        xs = np.linspace(0, 1, xb - xa); xs = xs if not rtl else xs[::-1]
        face = np.array([246, 247, 248.]) * (1.0 - 0.05 * xs)[None, :, None] * np.linspace(1.0, 0.95, h)[:, None, None]
        a[yt:by, xa:xb] = face
        out = Image.fromarray(a.clip(0, 255).astype(np.uint8))
        dr = ImageDraw.Draw(out)
        top = [(xa, yt), (xb, yt), (xb + dx, yt - dy), (xa + dx, yt - dy)]
        dr.polygon(top, fill=(253, 253, 253))
        side_x = xb if not rtl else xa
        side = [(side_x, yt), (side_x + dx, yt - dy), (side_x + dx, by - dy), (side_x, by)]
        dr.polygon(side, fill=(222, 226, 231))
        dr.line([(xa, yt), (xb, yt)], fill=(232, 234, 237), width=1)        # crisp front edge
        return (cx + dx / 2, yt - dy * 0.55, w)

    for k in ORDER:
        topx, topy, w = cube(k)
        keys = ON[k]; front = CUBES[k][3] == 1
        hs = [u * REAL_H[q] * (1.0 if front else 0.92) for q in keys]
        ws = [P[q].width * hh / P[q].height for q, hh in zip(keys, hs)]
        gap = u * 0.06
        kf = min(1.0, (w * 0.92) / (sum(ws) + gap * (len(keys) - 1)))
        hs = [hh * kf for hh in hs]; ws = [ww * kf for ww in ws]
        total = sum(ws) + gap * kf * (len(keys) - 1); rel = -total / 2
        for q, hh, ww in zip(keys, hs, ws):
            c = topx + (rel + ww / 2) * sgn; rel += ww + gap * kf
            # product shadow on the cube top + soft cast shadow
            sh_im = Image.new("RGBA", (int(ww * 1.2), max(4, int(ww * 0.16))), (0, 0, 0, 0))
            ImageDraw.Draw(sh_im).ellipse((0, 0, sh_im.width, sh_im.height), fill=(60, 70, 80, 70))
            sh_im = sh_im.filter(ImageFilter.GaussianBlur(max(1.5, ww * 0.04)))
            out.paste(sh_im, (int(c - sh_im.width / 2 + ww * 0.12 * sgn), int(topy - sh_im.height * 0.5)), sh_im)
            rim = P[q].resize((int(ww), int(hh)), Image.LANCZOS)
            alpha = rim.getchannel("A").point(lambda v: 0 if v < 24 else v)
            out.paste(rim.convert("RGB"), (int(c - ww / 2), int(topy - hh)), alpha)
    # green leaf sprig resting at the front
    lf = leaf_sprig(u / 190, rtl)
    lx = X(leaf[0]) - lf.width / 2; ly = base_front - lf.height * leaf[1]
    shadow = lf.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.35))
    out.paste((60, 70, 60), (int(lx + 6 * sgn), int(ly + 8)), shadow)
    out.paste(lf, (int(lx), int(ly)), lf)
    return out

SIZES = {  # W, H, x0, x1, base_back, base_front, hmax, u
    "1440x300": (1440, 300, 700, 1405, 266, 292, 140, 118),
    "706x320": (706, 320, 316, 700, 284, 312, 150, 100),
    "800x200": (800, 200, 398, 792, 178, 196, 86, 72),
    "800x1200": (800, 1200, 40, 760, 1050, 1150, 480, 270),
}
if __name__ == "__main__":
    for name, (W, H, x0, x1, bb, bf, hm, u) in SIZES.items():
        for rtl in (False, True):
            build(W, H, x0, x1, bb, bf, hm, u, rtl).save(here / f"products/offer2-bg-{name}-{'ar' if rtl else 'en'}.jpg", quality=93)
