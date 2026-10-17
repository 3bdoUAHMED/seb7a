"""Offer-2 final banners: navy headline -> yellow (with a soft dark shadow for legibility) and
red ribbons -> yellow. Logo, Yellow November sticker and products are left untouched.
Usage: python3 recolor-offer2.py <images dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I = sys.argv[1]
JOBS = {  # src: (name, text box (only bluish pixels inside it change), boxes protected from the ribbon recolour)
    50: ("mobile-ar-800x1200", (250, 40, 625, 400), [(30, 360, 215, 565), (60, 415, 780, 1060), (230, 30, 570, 60)]),
    51: ("desktop-ar-1440x300", (900, 30, 1235, 292), [(1235, 20, 1415, 100), (1240, 90, 1405, 235), (40, 30, 835, 255)]),
    52: ("mobile-ar-706x320", (440, 135, 640, 318), [(555, 12, 700, 58), (585, 55, 700, 132), (0, 40, 425, 320)]),
    53: ("mobile-ar-800x200", (440, 42, 712, 198), [(680, 5, 800, 52), (705, 52, 800, 150), (0, 25, 455, 200)]),
}
GOLD = np.array([245, 190, 20], np.float32)
os.makedirs("output/offer-2-final", exist_ok=True)
for n, (name, (tx0, ty0, tx1, ty1), prot) in JOBS.items():
    im = np.asarray(Image.open(f"{I}/{n}.jpg").convert("RGB")).astype(np.float32)
    out = im.copy()
    # --- navy text -> gold, anti-aliasing preserved via a coverage estimate against the local background
    reg = im[ty0:ty1, tx0:tx1]
    lum = reg.mean(2)
    blum = cv2.medianBlur(lum.astype(np.uint8), 61).astype(np.float32)        # background brightness
    navy = np.array([16, 52, 96], np.float32)
    bluish = (reg[..., 2] - reg[..., 0]) > 12
    cov = np.clip((blum - lum) / np.maximum(blum - navy.mean(), 1), 0, 1) * bluish
    cov = cv2.GaussianBlur(cov, (0, 0), 0.6)
    # remove the navy contribution and put gold in its place; background stays untouched
    base = reg + cov[..., None] * (GOLD - navy)
    shadow = np.roll(np.roll(cov, 3, 0), 2, 1); shadow = cv2.GaussianBlur(shadow, (0, 0), 1.5) * (1 - cov)
    base = base * (1 - 0.32 * shadow[..., None])
    out[ty0:ty1, tx0:tx1] = base
    # --- red ribbons -> yellow (outside protected areas)
    hsvf = cv2.cvtColor(out.clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    h, s, v = [hsvf[..., i].astype(int) for i in range(3)]
    allow = np.ones(h.shape, bool)
    for x0, y0, x1, y1 in prot: allow[y0:y1, x0:x1] = False
    red = (h < 10) | (h > 170)
    seed = (allow & red & (s > 140) & (v > 140)).astype(np.uint8)
    zone = cv2.dilate(seed, np.ones((5, 5), np.uint8)) > 0
    keep = allow & red & ((seed > 0) | (zone & (s > 70) & (v > 60)) | ((s > 30) & (v > 205)))
    hsvf[..., 0][keep] = 24
    hsvf[..., 1][keep] = np.clip(np.maximum(s[keep], 170) * 0.95, 0, 255)
    hsvf[..., 2][keep] = np.clip(v[keep] * 1.1 + 10, 0, 255)
    Image.fromarray(cv2.cvtColor(hsvf, cv2.COLOR_HSV2RGB)).save(f"output/offer-2-final/{name}.png")
