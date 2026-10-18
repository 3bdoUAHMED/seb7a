"""Offer-2 final banners: navy headline -> yellow (with a soft dark shadow for legibility) and
red ribbons -> yellow. Logo, Yellow November sticker and products are left untouched.
Usage: python3 recolor-offer2.py <images dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image
I = sys.argv[1]
JOBS = {  # src: (name, text box (only bluish pixels inside it change), boxes protected from the ribbon recolour)
    50: ("mobile-ar-800x1200", (200, 40, 625, 400), [(20, 355, 232, 592), (60, 455, 780, 1060), (238, 385, 284, 455), (342, 412, 428, 455), (490, 460, 580, 470)]),
    51: ("desktop-ar-1440x300", (900, 30, 1235, 292), [(1245, 25, 1405, 68), (1240, 90, 1405, 235), (40, 30, 835, 255)]),
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
    # whole ribbons at once (incl. their pink highlights), so none ends up half red / half yellow
    redh = (h < 12) | (h > 165)
    cand = (allow & redh & (s > 25) & (v > 70)).astype(np.uint8)
    nl, lab, st, _ = cv2.connectedComponentsWithStats(cand, 8)
    strong = allow & redh & (s > 140) & (v > 140)
    keep = np.zeros(h.shape, bool)
    for i in range(1, nl):
        comp = lab == i
        if strong[comp].sum() >= 15: keep |= comp
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & allow & redh & (s > 20)
    hsvf[..., 0][keep] = 24
    hsvf[..., 1][keep] = np.clip(s[keep] * 1.25 + 60, 0, 235)
    hsvf[..., 2][keep] = np.clip(v[keep] * 1.05 + 8, 0, 255)
    Image.fromarray(cv2.cvtColor(hsvf, cv2.COLOR_HSV2RGB)).save(f"output/offer-2-final/{name}.png")

# --- vertical banner: replace the hand-made red "Yellow Novmber" sticker with the clean yellow one
def replace_sticker(path, box, sticker_png, width, at, angle):
    im = np.asarray(Image.open(path).convert("RGB")).copy()
    x0, y0, x1, y1 = box
    reg = im[y0:y1, x0:x1]
    # wall model: smooth plane fitted to the box border, sticker = pixels that differ from it
    hh, ww = reg.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    border = np.zeros((hh, ww), bool); border[:4] = border[-4:] = True; border[:, :4] = border[:, -4:] = True
    A = np.stack([np.ones(border.sum()), xx[border], yy[border], xx[border] * yy[border]], 1)
    plane = np.zeros(reg.shape, np.float32)
    for c in range(3):
        co = np.linalg.lstsq(A, reg[..., c][border].astype(np.float32), rcond=None)[0]
        plane[..., c] = co[0] + co[1] * xx + co[2] * yy + co[3] * xx * yy
    diff = np.abs(reg.astype(np.float32) - plane).sum(2)
    sm = cv2.dilate((diff > 40).astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
    sm = cv2.GaussianBlur(sm.astype(np.float32), (0, 0), 3)[..., None]
    grain = reg.astype(np.float32) - cv2.GaussianBlur(reg.astype(np.float32), (0, 0), 3)
    reg[:] = (reg * (1 - sm) + (plane + grain * 0.0) * sm).clip(0, 255).astype(np.uint8)
    m = np.zeros(im.shape[:2], np.uint8)
    im = cv2.inpaint(im, m, 12, cv2.INPAINT_TELEA)
    out = Image.fromarray(im)
    st = Image.open(sticker_png).convert("RGBA")
    st = st.crop(st.getchannel("A").getbbox())
    st = st.resize((width, int(st.height * width / st.width)), Image.LANCZOS).rotate(angle, expand=True, resample=Image.BICUBIC)
    out.paste(st, at, st)
    out.save(path)

replace_sticker("output/offer-2-final/mobile-ar-800x1200.png", (20, 360, 232, 590), "products/sticker-yellow-november.png", 190, (22, 380), 0)
