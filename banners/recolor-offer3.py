"""Recolours the red word/ribbons/confetti/line of the supplied offer-3 (50%) banners to yellow,
leaving the products, logo and button as they are. Usage: python3 recolor-offer3.py <images dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I = sys.argv[1]
JOBS = {  # source -> (output, areas to leave untouched)
    42: ("desktop-ar-1440x300", [(615, 35, 725, 290), (720, 55, 990, 285), (1020, 25, 1070, 280), (228, 200, 412, 258), (1155, 25, 1415, 90)]),
    43: ("mobile-ar-706x320", [(12, 22, 138, 58), (322, 78, 422, 320), (402, 165, 706, 318), (645, 175, 706, 320), (78, 208, 232, 258)]),
    44: ("mobile-ar-800x200", [(252, 8, 326, 200), (322, 12, 515, 200), (520, 20, 552, 200), (628, 22, 788, 62), (68, 118, 196, 164)]),
    45: ("mobile-ar-800x1200", [(238, 38, 562, 122), (72, 525, 222, 925), (252, 615, 628, 890), (670, 562, 735, 915),
                                (0, 915, 800, 1200)]),
}
JOBS_EN = {
    46: ("desktop-en-1440x300", [(615, 35, 725, 290), (720, 55, 990, 285), (1020, 25, 1070, 280), (228, 162, 412, 214), (1155, 25, 1415, 90)]),
    47: ("mobile-en-706x320", [(12, 22, 138, 58), (322, 78, 422, 320), (402, 165, 706, 318), (645, 90, 706, 320), (78, 183, 232, 224)]),
    48: ("mobile-en-800x200", [(255, 12, 330, 200), (322, 12, 515, 200), (520, 20, 552, 200), (628, 45, 788, 90), (68, 90, 196, 122)]),
    49: ("mobile-en-800x1200", [(238, 38, 562, 122), (72, 525, 222, 925), (252, 615, 628, 890), (670, 555, 735, 915), (0, 915, 800, 1200)]),
}
if len(sys.argv) > 2 and sys.argv[2] == "en": JOBS = JOBS_EN
# confetti ribbons lying over the products (only the ribbon itself is picked inside these boxes: its red has
# B ~ G, the magenta product label has B well above G)
RIBBONS = {43: [(284, 222, 390, 272)], 44: [(236, 24, 284, 70), (252, 134, 308, 177)], 45: [(158, 548, 226, 616)],
           42: [(414, 170, 482, 258)]}


PROTECT = {44: [(255, 130, 320, 200)], 43: [(325, 255, 395, 320)]}   # product labels: never recolour


def to_yellow(im, keep, allow_ext):
    """red -> yellow by "redness" (R - G) so shading, highlights and anti-aliasing survive; the outline is
    re-blended against the wall (each edge pixel = a * ribbon + (1 - a) * wall) so it stays smooth."""
    o = im.astype(np.float32)
    k3 = np.ones((3, 3), np.uint8)
    near = lambda m, r: cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)).astype(bool)
    rg = np.clip(o[..., 0] - np.maximum(o[..., 1], o[..., 2]), 0, None)
    # thin ribbon tips and soft ends: strongly red pixels touching what was found
    obj = keep.copy()
    # (the beige wall always has B well below G; red / pink ribbon pixels have B ~ G)
    bg = o[..., 2] - o[..., 1]
    ribbonish = (o[..., 0] - o[..., 1] > 28) & (bg > -16) & (bg < 22)   # wall: R - G < 22; magenta label: B - G > 22
    for _ in range(8): obj |= near(obj, 1) & allow_ext & ribbonish
    y = o.copy()
    y[..., 0] = o[..., 0] + 0.08 * rg
    y[..., 1] = o[..., 1] + 0.86 * rg
    y[..., 2] = o[..., 2] - 0.25 * rg
    res = np.where(obj[..., None], y, o)
    core = cv2.erode(obj.astype(np.uint8), k3).astype(bool)
    band = near(obj, 2) & allow_ext & ~core
    def fill(img, mask):
        return np.dstack([cv2.inpaint(img[..., c].astype(np.float32), mask.astype(np.uint8), 3, cv2.INPAINT_TELEA)
                          for c in range(3)])
    Fr = fill(o, ~core & near(obj, 4))            # ribbon colour carried out from inside
    Dl = fill(y - o, ~core & near(obj, 4))        # its red -> yellow change
    B = fill(o, near(obj, 2) & near(obj, 6))      # wall colour carried in from outside
    e = Fr - B
    a = np.clip(((o - B) * e).sum(2) / np.maximum((e * e).sum(2), 1), 0, 1)
    a = np.where(band, cv2.GaussianBlur(a.astype(np.float32), (0, 0), 0.6), a)
    nw = o + a[..., None] * Dl
    nw[..., 1] = np.minimum(nw[..., 1], np.maximum(0.9 * nw[..., 0], o[..., 1]))   # never greener than the yellow
    res[band] = nw[band]
    return res.clip(0, 255).astype(np.uint8)


os.makedirs("output/offer-3-final", exist_ok=True)
for n, (name, skip) in JOBS.items():
    p = next(f for f in (f"{I}/{n}.png", f"{I}/{n}.webp") if os.path.exists(f))
    im = np.asarray(Image.open(p).convert("RGB")).copy()
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    allow = np.ones(h.shape, bool)
    for x0, y0, x1, y1 in skip: allow[y0:y1, x0:x1] = False
    red = (h < 10) | (h > 170)
    seed = (allow & red & (s > 140) & (v > 150)).astype(np.uint8)
    r = max(2, int(min(h.shape) * 0.007))
    zone = cv2.dilate(seed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0
    keep = allow & red & ((seed > 0) | (zone & (s > 80) & (v > 60)) | ((s > 30) & (v > 205)))
    # confetti lying over the products: only the very bright, saturated ribbon red (product reds are deeper)
    over = (~allow) & red & (s > 185) & (v > 215)
    for x0, y0, x1, y1 in PROTECT.get(n, []): over[y0:y1, x0:x1] = False
    over = cv2.morphologyEx(over.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
    near = cv2.dilate(over.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    keep = keep | over | (near & red & (s > 120) & (v > 120))
    for x0, y0, x1, y1 in PROTECT.get(n, []): keep[y0:y1, x0:x1] = False
    o = im.astype(int)
    rib_red = (o[..., 0] - o[..., 1] > 60) & (o[..., 2] - o[..., 1] < 18) & (o[..., 0] > 170)   # (button: darker)
    ribs = np.zeros(h.shape, bool)
    for x0, y0, x1, y1 in RIBBONS.get(n, []):
        box = np.zeros(h.shape, bool); box[y0:y1, x0:x1] = True
        nl, lab, st, _ = cv2.connectedComponentsWithStats((box & rib_red).astype(np.uint8), 8)
        ribs |= np.isin(lab, [i for i in range(1, nl) if st[i, 4] >= 30])
    keep |= ribs
    ext = (allow | keep | cv2.dilate(ribs.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool))
    out = to_yellow(im, keep, allow_ext=ext).astype(np.float32)
    # ribbons crossing a product are only a few pixels wide: recolour them softly, each pixel by how much
    # "ribbon red" it holds (B ~ G and R >> G) -- the magenta label (B well above G) gets weight 0
    of = im.astype(np.float32)
    bg, rgd = of[..., 2] - of[..., 1], of[..., 0] - of[..., 1]
    t = np.clip((14 - bg) / 12, 0, 1) * np.clip((rgd - 35) / 55, 0, 1)   # (label's muted red strip: B - G ~ 14+)
    rgn = np.clip(of[..., 0] - np.maximum(of[..., 1], of[..., 2]), 0, None)
    soft = of.copy()
    soft[..., 0] += 0.08 * rgn * t; soft[..., 1] += 0.86 * rgn * t; soft[..., 2] -= 0.25 * rgn * t
    for x0, y0, x1, y1 in RIBBONS.get(n, []):
        reg = np.zeros(h.shape, bool); reg[y0:y1, x0:x1] = True
        reg &= cv2.dilate((t > 0.5).astype(np.uint8) & reg.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        out[reg] = soft[reg]
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(f"output/offer-3-final/{name}.png")
