import sys, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
im = cv2.imread(src)  # BGR
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
white = (np.minimum(np.minimum(r, g), b) > 228)
neutral_dark = (np.abs(r - b) < 20) & (r < 205)
red = (r - g > 60)
m = (white | neutral_dark | red).astype(np.uint8) * 255
box = np.zeros_like(m); box[160:560, 170:735] = 255
m = cv2.bitwise_and(m, box)
m = cv2.dilate(m, np.ones((7, 7), np.uint8), iterations=2)
cv2.imwrite(out.replace('.png', '-mask.png'), m)
res = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
cv2.imwrite(out, res)
