"""Recolours the red word/ribbons/confetti/line of the supplied offer-3 (50%) banners to yellow,
leaving the products, logo and button as they are. Usage: python3 recolor-offer3.py <images dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I = sys.argv[1]
JOBS = {  # source -> (output, areas to leave untouched)
    42: ("desktop-ar-1440x300", [(615, 35, 725, 290), (720, 55, 990, 285), (1020, 25, 1070, 280), (228, 200, 412, 258), (1155, 25, 1415, 102)]),
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


YELLOW = np.array([255, 212, 36], np.float32)   # same bright yellow as the Yellow November sticker
CREAM = np.array([255, 246, 190], np.float32)    # what the pale pink highlights become


def ymap(o):
    """the yellow version of a red pixel: its brightness comes from R, its pink highlight (G, B rising
    towards R) becomes a cream highlight"""
    R, G = o[..., 0], o[..., 1]
    shade = np.clip(R / 232, 0, 1)[..., None]
    w = np.clip((G - 0.28 * R) / np.maximum(0.72 * R, 1), 0, 1)[..., None]
    # darker tones turn warm golden brown (green falls off faster), not olive
    dark = YELLOW * np.concatenate([shade, shade ** 1.35, shade ** 2.2], -1)
    return dark * (1 - w) + CREAM * shade * w


def redness(o):
    """0..1: how much of the pixel is ribbon red. The beige wall has R - G < 22; the magenta product
    label / burgundy button have B well above G; the ribbons have B ~ G and R far above G."""
    bg, rgd = o[..., 2] - o[..., 1], o[..., 0] - o[..., 1]
    return np.clip((14 - bg) / 12, 0, 1) * np.clip((rgd - 28) / 50, 0, 1)


def to_yellow(im, keep, allow_ext):
    """red -> yellow keeping shading and highlights; ribbon outlines are re-blended against the wall
    (each edge pixel = a * ribbon + (1 - a) * wall) so they stay as smooth as the original."""
    o = im.astype(np.float32)
    k3 = np.ones((3, 3), np.uint8)
    near = lambda m, r: cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)).astype(bool)
    t = redness(o)
    # everything ribbon-red (thin tips included), plus the pink highlights touching it
    cand = allow_ext & (t > 0.3)
    nl, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), 8)
    obj = keep | np.isin(lab, [i for i in range(1, nl) if st[i, 4] >= 8])
    bg = o[..., 2] - o[..., 1]
    pinkish = (o[..., 0] - o[..., 1] > 20) & (bg > -14) & (bg < 22) & (o[..., 0] > 150)
    for _ in range(6): obj |= near(obj, 1) & allow_ext & pinkish
    # things that are already yellow / gold / white-on-yellow (the Yellow November sticker) stay exactly as they are
    R_, G_, B_ = o[..., 0], o[..., 1], o[..., 2]
    gold = (G_ > 0.6 * R_) & (B_ < 0.75 * G_) & (R_ > 140) & (R_ - B_ > 70)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(gold.astype(np.uint8), 8)
    gold = np.isin(lab2, [i for i in range(1, n2) if st2[i, 4] >= 150])     # big gold areas only, not ribbon pixels
    hands_off = near(gold, 3)
    obj &= ~hands_off
    allow_ext = allow_ext & ~hands_off
    y = ymap(o)
    res = np.where(obj[..., None], y, o)
    core = cv2.erode(obj.astype(np.uint8), k3).astype(bool)
    band = near(obj, 2) & allow_ext & ~core
    def fill(img, mask):
        return np.dstack([cv2.inpaint(img[..., c].astype(np.float32), mask.astype(np.uint8), 3, cv2.INPAINT_TELEA)
                          for c in range(3)])
    Fr = fill(o, ~core & near(obj, 4))            # ribbon colour carried out from inside
    Fy = fill(y, ~core & near(obj, 4))            # ... and its yellow version
    B = fill(o, near(obj, 2) & near(obj, 6))      # wall colour carried in from outside
    e = Fr - B
    a = np.clip(((o - B) * e).sum(2) / np.maximum((e * e).sum(2), 1), 0, 1)
    a = np.where(band, cv2.GaussianBlur(a.astype(np.float32), (0, 0), 0.6), a)
    a = np.where(obj, np.maximum(a, t), a)        # a clearly red pixel is all ribbon (thin tips)
    a3 = a[..., None]
    # edge pixel: take its ribbon part out (a * Fr) and put the yellow one in (a * Fy)
    nw = o + a3 * (Fy - Fr)
    nw = np.where(obj[..., None] & (t[..., None] > 0.8), y, nw)
    nw[..., 1] = np.minimum(nw[..., 1], np.maximum(0.86 * nw[..., 0], o[..., 1]))   # no green fringe
    res[band] = nw[band]
    return res.clip(0, 255).astype(np.uint8), hands_off


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
    out, hands_off = to_yellow(im, keep, allow_ext=ext)
    out = out.astype(np.float32)
    # ribbons crossing a product are only a few pixels wide: recolour them softly, each pixel by how much
    # "ribbon red" it holds (B ~ G and R >> G) -- the magenta label (B well above G) gets weight 0
    of = im.astype(np.float32)
    t = redness(of)
    soft = of + t[..., None] * (ymap(of) - of)
    for x0, y0, x1, y1 in RIBBONS.get(n, []):
        reg = np.zeros(h.shape, bool); reg[y0:y1, x0:x1] = True
        reg &= cv2.dilate((t > 0.5).astype(np.uint8) & reg.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        out[reg] = soft[reg]
    out[hands_off] = of[hands_off]
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(f"output/offer-3-final/{name}.png")
