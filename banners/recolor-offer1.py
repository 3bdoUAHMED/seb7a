"""Recolours the red 3D 40% and the floating squiggles to yellow in the supplied offer-1 banners
(only inside the given areas, so the red products and the SALE ribbon stay red) and adds the
Yellow November sticker where it is missing. Usage: python3 recolor-offer1.py <images dir> <sticker.png>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I, STK = sys.argv[1], sys.argv[2]
JOBS = {  # source -> (output name, allowed areas (x0,y0,x1,y1), sticker (x,y,width) or None)
    34: ("desktop-ar-1440x300", [(25, 35, 275, 235), (855, 28, 910, 68), (145, 245, 200, 280)], None),
    35: ("mobile-ar-706x320", [(130, 222, 305, 320), (365, 8, 415, 42), (10, 265, 55, 298)], (14, 8, 150)),
    36: ("mobile-ar-800x200", [(10, 0, 120, 100), (50, 150, 90, 180)], (528, 6, 104)),
    37: ("mobile-en-800x1200", [(150, 745, 655, 1005), (685, 285, 745, 340), (75, 900, 170, 955),
                                (605, 955, 695, 1015), (15, 1105, 100, 1165), (675, 1090, 735, 1160)], None),
}
JOBS_EN = {
    38: ("desktop-en-1440x300", [(1245, 110, 1425, 275), (530, 30, 580, 68), (1240, 245, 1295, 280)], None),
    39: ("mobile-en-706x320", [(420, 235, 605, 320), (290, 8, 340, 40), (650, 258, 695, 292)], (556, 8, 140)),
    40: ("mobile-en-800x200", [(660, 0, 800, 100), (710, 155, 755, 185)], (250, 4, 90)),
    41: ("mobile-en-800x1200", [(150, 745, 655, 1005), (685, 285, 745, 340), (75, 900, 170, 955),
                                (605, 955, 695, 1015), (15, 1105, 100, 1165), (675, 1090, 735, 1160)], None),
}
if len(sys.argv) > 3 and sys.argv[3] == "en": JOBS = JOBS_EN
stk = Image.open(STK); stk = stk.crop(stk.getchannel("A").getbbox())
os.makedirs("output/offer-1-final", exist_ok=True)
for n, (name, areas, place) in JOBS.items():
    p = next(f for f in (f"{I}/{n}.png", f"{I}/{n}.webp") if os.path.exists(f))
    im = np.asarray(Image.open(p).convert("RGB")).copy()
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    allow = np.zeros(h.shape, bool)
    for x0, y0, x1, y1 in areas: allow[y0:y1, x0:x1] = True
    red = (h < 10) | (h > 170)
    # grow from the bright red faces only, so the dark burgundy floor around them is left alone
    seed = (allow & red & (s > 150) & (v > 165)).astype(np.uint8)
    r = max(2, int(min(h.shape) * 0.007))
    zone = cv2.dilate(seed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0
    keep = allow & red & ((seed > 0) | ((s > 25) & (v > 200)) | (zone & (s > 80) & (v > 60)))
    hsv[..., 0][keep] = 24
    hsv[..., 1][keep] = np.clip(np.maximum(s[keep], 170) * 0.95, 0, 255)
    hsv[..., 2][keep] = np.clip(v[keep] * 1.08 + 8, 0, 255)
    out = Image.fromarray(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB))
    if place:
        x, y, w = place; s2 = stk.resize((w, int(stk.height * w / stk.width)), Image.LANCZOS); out.paste(s2, (x, y), s2)
    out.save(f"output/offer-1-final/{name}.png")
