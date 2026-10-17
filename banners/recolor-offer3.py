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
    45: ("mobile-ar-800x1200", [(238, 38, 562, 122), (72, 525, 222, 925), (252, 615, 628, 890), (670, 555, 735, 915),
                                (0, 915, 800, 1200)]),
}
JOBS_EN = {
    46: ("desktop-en-1440x300", [(615, 35, 725, 290), (720, 55, 990, 285), (1020, 25, 1070, 280), (228, 162, 412, 214), (1155, 25, 1415, 90)]),
    47: ("mobile-en-706x320", [(12, 22, 138, 58), (322, 78, 422, 320), (402, 165, 706, 318), (645, 90, 706, 320), (78, 183, 232, 224)]),
    48: ("mobile-en-800x200", [(255, 12, 330, 200), (322, 12, 515, 200), (520, 20, 552, 200), (628, 45, 788, 90), (68, 90, 196, 122)]),
    49: ("mobile-en-800x1200", [(238, 38, 562, 122), (72, 525, 222, 925), (252, 615, 628, 890), (670, 555, 735, 915), (0, 915, 800, 1200)]),
}
if len(sys.argv) > 2 and sys.argv[2] == "en": JOBS = JOBS_EN
# small confetti ribbons that sit on top of the products (recoloured fully inside these boxes)
RIBBONS = {43: [(300, 160, 340, 200), (320, 245, 350, 275)], 44: [(240, 40, 262, 75)], 45: [(170, 555, 220, 610)],
           42: [(410, 180, 480, 245)]}
PROTECT = {44: [(255, 130, 320, 200)], 43: [(325, 255, 395, 320)]}   # product labels: never recolour
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
    for x0, y0, x1, y1 in RIBBONS.get(n, []):
        box = np.zeros(h.shape, bool); box[y0:y1, x0:x1] = True
        keep |= box & red & (s > 110) & (v > 110)
    for x0, y0, x1, y1 in PROTECT.get(n, []): keep[y0:y1, x0:x1] = False
    hsv[..., 0][keep] = 24
    hsv[..., 1][keep] = np.clip(np.maximum(s[keep], 170) * 0.95, 0, 255)
    hsv[..., 2][keep] = np.clip(v[keep] * 1.1 + 10, 0, 255)
    Image.fromarray(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)).save(f"output/offer-3-final/{name}.png")
