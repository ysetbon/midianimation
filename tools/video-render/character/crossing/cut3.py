# Cut the 32 chase poses (white sheet 23, black sheet 27) from their transparent
# 4x4 sheets. Each opaque blob goes to the cell its centre falls in, so puffs and
# speed lines that cross the nominal cell borders stay with their pose. The white
# one's grey ground shadow becomes pure darkness (it takes the background's colour).
# Anchors: gy = the ground line (shadow, or the lowest foot), gx = the body's centre.
import numpy as np, json, sys
from PIL import Image
from scipy import ndimage
import os
D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
IMG = D + '/../sheets/'
SHEETS = {'W': IMG + 'white_chase.webp', 'K': IMG + 'black_chase.png'}   # W: the tall-card redraw chosen on 2026-10-25
out, anchors = {}, {}
for name, path in SHEETS.items():
    a = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32) / 255
    H, W = a.shape[:2]; ch, cw = H / 4, W / 4
    al = a[:, :, 3].copy(); al[al < 0.04] = 0
    # where a pose touches the one below it (a cap against the feet above), cut along the
    # emptiest line near the cell border, within each column of cells
    cuts = []
    for c in range(4):
        xa, xb = int(c * cw), int((c + 1) * cw)
        for r in (1, 2, 3):
            yb = int(r * ch); band = (al[yb - 50:yb + 50, xa:xb] > 0.04).sum(1)
            y = yb - 50 + int(np.argmin(band + np.abs(np.arange(100) - 50))); al[y, xa:xb] = 0; cuts.append((y, xa, xb))   # emptiest, but near the border
    lab, n = ndimage.label(al > 0.04, structure=np.ones((3, 3)))
    cms = ndimage.center_of_mass(al > 0.04, lab, range(1, n + 1))
    cell = np.zeros(n + 1, int) - 1
    for k, (cy, cx) in enumerate(cms, 1):
        cell[k] = min(3, int(cy // ch)) * 4 + min(3, int(cx // cw))
    # a small piece cut off by the line (the tip of a shoe) belongs with the pose across the line
    areas = ndimage.sum(np.ones_like(al), lab, range(1, n + 1))
    for k in range(1, n + 1):
        if areas[k - 1] > 8000: continue
        ys, xs = np.nonzero(lab == k)
        for y, xa, xb in cuts:
            if not (xa <= xs.mean() < xb): continue
            other = lab[y - 1, xs.min():xs.max() + 1] if ys.min() == y + 1 else lab[y + 1, xs.min():xs.max() + 1] if ys.max() == y - 1 else None
            if other is not None and (other > 0).any(): cell[k] = cell[np.bincount(other[other > 0]).argmax()]
    cl = cell[lab]; cl[lab == 0] = -1
    for y, xa, xb in cuts:   # the cut line itself goes back to whichever pose it touches
        row = cl[y, xa:xb]; up, dn = cl[y - 1, xa:xb], cl[y + 1, xa:xb]
        fill = (a[y, xa:xb, 3] > 0.04) & (row < 0)
        row[fill] = np.where(up[fill] >= 0, up[fill], dn[fill])
    for c in range(16):
        m = cl == c
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
        y0, x0 = max(0, y0), max(0, x0)
        t = a[y0:y1, x0:x1].copy(); mm = m[y0:y1, x0:x1]
        rgb, al2 = t[:, :, :3], np.where(mm, t[:, :, 3], 0)
        lum = rgb.mean(2); sat = rgb.max(2) - rgb.min(2)
        if name == 'W':
            low = np.arange(t.shape[0])[:, None] >= int(t.shape[0] * 0.7)
            shadow = low & (sat < 0.12) & (lum > 0.12) & (lum < 0.75) & (al2 < 0.97) & (al2 > 0)   # the soft grey ellipse under the feet
            rgb[shadow] = 0
            body = (al2 > 0.9) & (rgb[:, :, 0] > 0.8) & (rgb[:, :, 1] > 0.65) & (rgb[:, :, 2] > 0.55)
            # stand on the soles; only a pose in the air (feet well above its shadow) uses the shadow's centre
            feet = int(np.nonzero(((al2 > 0.8) & ~shadow).any(1))[0].max())
            sc = int(np.argmax(shadow.sum(1)))
            gy = sc if shadow.sum() > 150 and sc - feet > 25 else feet
        else:
            body = (al2 > 0.9) & (rgb.max(2) < 0.22) & (rgb[:, :, 2] > rgb[:, :, 0])   # the dark navy body (not the pure black shoes)
            gy = int(np.nonzero(al2 > 0.5)[0].max())
        by, bx = np.nonzero(body)
        k = f'{name}_{c + 1}'
        out[k + '_rgb'] = (rgb * 255 + 0.5).astype(np.uint8); out[k + '_a'] = (al2 * 255 + 0.5).astype(np.uint8)
        anchors[k] = {'gx': float(bx.mean()), 'gy': gy, 'bodyH': int(by.max() - by.min()), 'bodyW': int(bx.max() - bx.min()),
                      'bodyTop': int(by.min()), 'w': int(t.shape[1]), 'h': int(t.shape[0])}
np.savez_compressed(D + '/chase_sprites.npz', **out); json.dump(anchors, open(D + '/chase_anchors.json', 'w'), indent=0)
for k in ('W_1', 'W_5', 'K_1', 'K_16'): print(k, anchors[k])
