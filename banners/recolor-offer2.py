"""Offer-2 final banners: navy headline -> yellow (with a soft dark shadow for legibility) and
red ribbons -> yellow. Logo, Yellow November sticker and products are left untouched.
Usage: python3 recolor-offer2.py <images dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I = sys.argv[1]
JOBS = {  # src: (name, text box (only bluish pixels inside it change), boxes protected from the ribbon recolour)
    50: ("mobile-ar-800x1200", (200, 40, 625, 400), [(30, 360, 215, 565), (60, 415, 780, 1060), (230, 30, 570, 60)]),
    51: ("desktop-ar-1440x300", (900, 30, 1235, 292), [(1235, 20, 1415, 100), (1240, 90, 1405, 235), (40, 30, 835, 255)]),
    52: ("mobile-ar-706x320", (440, 135, 640, 318), [(555, 12, 700, 58), (585, 55, 700, 132), (0, 40, 425, 320)]),
    53: ("mobile-ar-800x200", (440, 42, 712, 198), [(680, 5, 800, 52), (705, 52, 800, 150), (0, 25, 455, 200)]),
}
GOLD = np.array([128, 22, 42], np.float32)   # burgundy text (matches the logo)
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
    base = base * (1 - 0.12 * shadow[..., None])
    out[ty0:ty1, tx0:tx1] = base
    # --- the red "2" digits inside the text box -> same burgundy (large red blobs only; small ones are confetti)
    th = cv2.cvtColor(out[ty0:ty1, tx0:tx1].clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(int)
    rr = (((th[..., 0] < 10) | (th[..., 0] > 170)) & (th[..., 1] > 90) & (th[..., 2] > 70)).astype(np.uint8)
    DIGITS = {51: [(1015, 55, 1070, 125), (925, 185, 980, 250)], 52: [(510, 165, 550, 210), (450, 255, 490, 300)],
              53: [(535, 45, 580, 90), (475, 140, 515, 185)], 50: [(350, 100, 425, 185), (220, 300, 285, 375)]}
    digit = np.zeros(rr.shape, bool)
    for x0, y0, x1, y1 in DIGITS[n]: digit[max(0, y0 - ty0):y1 - ty0, max(0, x0 - tx0):x1 - tx0] = True
    # digits keep their original red (accent next to the burgundy words)
    digit_full = np.zeros(out.shape[:2], bool); digit_full[ty0:ty1, tx0:tx1] = digit
    # --- red ribbons -> yellow (outside protected areas)
    hsvf = cv2.cvtColor(out.clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    h, s, v = [hsvf[..., i].astype(int) for i in range(3)]
    allow = ~digit_full
    for x0, y0, x1, y1 in prot: allow[y0:y1, x0:x1] = False
    red = (h < 10) | (h > 170)
    seed = (allow & red & (s > 140) & (v > 140)).astype(np.uint8)
    zone = cv2.dilate(seed, np.ones((5, 5), np.uint8)) > 0
    keep = allow & red & ((seed > 0) | (zone & (s > 70) & (v > 60)) | ((s > 30) & (v > 205)))
    hsvf[..., 0][keep] = 24
    hsvf[..., 1][keep] = np.clip(np.maximum(s[keep], 170) * 0.95, 0, 255)
    hsvf[..., 2][keep] = np.clip(v[keep] * 1.1 + 10, 0, 255)
    Image.fromarray(cv2.cvtColor(hsvf, cv2.COLOR_HSV2RGB)).save(f"output/offer-2-final/{name}.png")

# --- vertical banner: the red "Yellow Novmber" sticker -> yellow ribbon/star with dark lettering
def sticker_to_yellow(path, box):
    im = np.asarray(Image.open(path).convert("RGB")).copy()
    x0, y0, x1, y1 = box
    reg = im[y0:y1, x0:x1]
    hsv = cv2.cvtColor(reg, cv2.COLOR_RGB2HSV).astype(int)
    red = (((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 90) & (hsv[..., 2] > 80)).astype(np.uint8)
    nl, lab, st, _ = cv2.connectedComponentsWithStats(red, 8)
    big = np.zeros(red.shape, np.uint8); small = np.zeros(red.shape, bool)
    for i in range(1, nl):
        if st[i, cv2.CC_STAT_AREA] > 400: big[lab == i] = 1
        elif st[i, cv2.CC_STAT_AREA] > 4: small |= lab == i
    # white letters inside the red ribbon = holes in the ribbon mask
    filled = big.copy(); cnts, _ = cv2.findContours(big, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    holes = (filled > 0) & (big == 0)
    yellow = np.array([245, 196, 30.]); ink = np.array([25, 25, 25.])
    shade = (reg.astype(np.float32).max(2) / 255.0)[..., None]
    out = reg.astype(np.float32)
    out[big > 0] = (yellow * np.clip(shade * 1.15, 0.75, 1.05))[big > 0]
    out[holes] = ink
    out[small] = ink
    # anti-aliased red fringes left on the letters -> blend toward ink
    fr = ((hsv[..., 0] < 12) | (hsv[..., 0] > 165)) & (hsv[..., 1] > 35) & (big == 0) & ~holes & ~small
    a = np.clip((hsv[..., 1] - 35) / 120.0, 0, 1)[..., None]
    out[fr] = (out * (1 - a) + ink * a)[fr]
    im[y0:y1, x0:x1] = out.clip(0, 255).astype(np.uint8)
    Image.fromarray(im).save(path)

sticker_to_yellow("output/offer-2-final/mobile-ar-800x1200.png", (25, 360, 220, 570))
