"""Offer-1 final banners: the red 3D 40% and the floating squiggles -> yellow, keeping all of their 3D
shading, highlights and soft edges; adds the Yellow November sticker where a banner has none.
Only red inside the given areas changes, so the red products, the floor and the SALE tag stay as they are.
Usage: python3 recolor-offer1.py <images dir> <sticker.png> [en]"""
import sys, os
import numpy as np, cv2
from PIL import Image
I, STK = sys.argv[1], sys.argv[2]
SQ = [(685, 285, 745, 340), (75, 900, 170, 955), (605, 955, 695, 1015), (15, 1105, 100, 1165), (675, 1090, 735, 1160)]
JOBS = {  # source -> (output name, allowed areas (x0,y0,x1,y1), sticker (x,y,width) or None)
    70: ("desktop-ar-1440x300", [(25, 35, 275, 235), (855, 28, 910, 68), (145, 245, 200, 280)], None),
    71: ("mobile-ar-706x320", [(130, 222, 305, 320), (365, 8, 415, 42), (10, 265, 55, 298)], (6, 4, 112)),
    72: ("mobile-ar-800x200", [(10, 0, 120, 100), (50, 150, 90, 180)], (500, 5, 86)),
    73: ("mobile-ar-800x1200", [(145, 760, 660, 1015), (55, 290, 110, 335), (115, 955, 190, 1010),
                                (635, 900, 720, 960), (70, 1090, 125, 1155), (695, 1115, 780, 1165)], None),
}
JOBS_EN = {
    38: ("desktop-en-1440x300", [(1245, 110, 1425, 275), (530, 30, 580, 68), (1240, 245, 1295, 280)], None),
    39: ("mobile-en-706x320", [(420, 235, 605, 320), (290, 8, 340, 40), (650, 258, 695, 292)], (556, 8, 140)),
    40: ("mobile-en-800x200", [(660, 0, 800, 100), (710, 155, 755, 185)], (250, 4, 90)),
    41: ("mobile-en-800x1200", [(150, 745, 655, 1005)] + SQ, None),
}
if len(sys.argv) > 3 and sys.argv[3] == "en": JOBS = JOBS_EN


def to_yellow(im, areas):
    o = im.astype(np.float32)
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    h, s, v = [hsv[..., i].astype(int) for i in range(3)]
    allow = np.zeros(h.shape, bool)
    for x0, y0, x1, y1 in areas: allow[y0:y1, x0:x1] = True
    redh = (h < 12) | (h > 165)
    R, G = o[..., 0], o[..., 1]
    nb = (o[..., 2] - G) < 7          # the burgundy floor (even its bright glow) has a blue tint (B > G); the 3D red doesn't
    k3 = np.ones((3, 3), np.uint8)
    def near(mask, r):
        return cv2.dilate(mask.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)).astype(bool)
    # 1) the lit faces of the 3D number / squiggles: bright and strongly red
    face = allow & redh & nb & (((s > 140) & (v > 150)) | ((s > 15) & (v > 175)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(face.astype(np.uint8), 8)
    face = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 25])
    face = cv2.morphologyEx(face.astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool) & allow
    # 2) the darker red rims where a face turns into its black side (must touch that black side)
    black = o.max(2) < 70
    rim = near(face, 6) & near(black, 3) & allow & redh & nb & (R > 55) & (G < 0.22 * R + 2)
    # 3) pinkish lips / reflections on the face edges: brighter than any floor pixel
    gr = G / np.maximum(R, 1)
    lip = near(face, 6) & allow & redh & nb & (s > 25) & (v > 130) & (gr > 0.36) & (gr < 0.85)  # pink, not floor/gold arc
    # 4) deep red shading inside the 3D (almost zero green -- darker floor pixels always carry some), grown from the faces
    deep = allow & redh & nb & (R > 45) & (G < 0.12 * R + 2)
    obj = face | rim | lip
    for _ in range(25): obj = obj | (cv2.dilate(obj.astype(np.uint8), k3).astype(bool) & deep)
    # 5) small red reflections / lines enclosed by the number's own body
    hull = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))).astype(bool)
    obj |= hull & allow & redh & nb & (s > 60) & (v > 50) & (G < 0.3 * R)
    obj = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_CLOSE, k3).astype(bool) & allow
    zone = near(obj, 1) & allow                                   # + 1px of soft edge
    # red -> yellow by "redness" (R - G): every pixel keeps its own brightness, highlight and edge blend
    rg = np.clip(o[..., 0] - np.maximum(o[..., 1], o[..., 2] * 0.9), 0, None)
    y = o.copy()
    y[..., 0] = o[..., 0] + 0.06 * rg
    y[..., 1] = o[..., 1] + 0.80 * rg
    y[..., 2] = o[..., 2] - 0.30 * rg
    # soft edge pixels change only as much as they are "pure red", so the floor around gets no glow
    purity = np.clip((0.25 - G / np.maximum(R, 1)) / 0.08, 0, 1) * nb
    m = cv2.GaussianBlur(zone.astype(np.float32), (0, 0), 0.7) * np.where(obj | near(black, 2), 1.0, purity)
    m = m[..., None]
    return (o * (1 - m) + y * m).clip(0, 255).astype(np.uint8)


stk = Image.open(STK); stk = stk.crop(stk.getchannel("A").getbbox())
os.makedirs("output/offer-1-final", exist_ok=True)
for n, (name, areas, place) in JOBS.items():
    p = next(f for f in (f"{I}/{n}.png", f"{I}/{n}.webp", f"{I}/{n}.jpg") if os.path.exists(f))
    im = np.asarray(Image.open(p).convert("RGB")).copy()
    out = Image.fromarray(to_yellow(im, areas))
    if place:
        x, y, w = place; s2 = stk.resize((w, int(stk.height * w / stk.width)), Image.LANCZOS); out.paste(s2, (x, y), s2)
    out.save(f"output/offer-1-final/{name}.png")
