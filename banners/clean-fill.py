"""Texture-aware fill: smooth light/shadow from a low-res inpaint + real wall grain.
Usage: python3 clean-fill.py src.png mask.png out.png grain_x0 grain_y0 grain_x1 grain_y1"""
import sys, cv2, numpy as np
src, mpath, out = sys.argv[1:4]
gx0, gy0, gx1, gy1 = map(int, sys.argv[4:8])
im = cv2.imread(src).astype(np.float32)
m = cv2.imread(mpath, 0)
h, w = m.shape
f = 6
small = cv2.resize(im, (w // f, h // f), interpolation=cv2.INTER_AREA).astype(np.uint8)
ms = cv2.resize(m, (w // f, h // f), interpolation=cv2.INTER_NEAREST)
ms = cv2.dilate(ms, np.ones((3, 3), np.uint8))
low = cv2.inpaint(small, ms, 6, cv2.INPAINT_NS)
low = cv2.resize(low, (w, h), interpolation=cv2.INTER_CUBIC).astype(np.float32)
low = cv2.GaussianBlur(low, (0, 0), 5)
# grain = high-pass of a clean patch, tiled with mirroring
patch = im[gy0:gy1, gx0:gx1]
grain = patch - cv2.GaussianBlur(patch, (0, 0), 4)
ph, pw = grain.shape[:2]
tile = np.concatenate([grain, grain[:, ::-1]], 1)
tile = np.concatenate([tile, tile[::-1]], 0)
reps = (h // tile.shape[0] + 1, w // tile.shape[1] + 1, 1)
g = np.tile(tile, reps)[:h, :w]
fill = low + g
a = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 3)[..., None]
res = im * (1 - a) + fill * a
cv2.imwrite(out, res.clip(0, 255).astype(np.uint8))
