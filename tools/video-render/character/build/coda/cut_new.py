# Cut the user's new sharp hug drawings (2026-11-01): 2x2 sheets S 1-4, T 1-4, R 1-4, K 1-4, M 1-4, N 1-4 and five single drawings U 1-5.
# Each is anchored on the White Key Piano's card (its centre) and the group's lowest foot, and sized so the group
# (feet to the top of the hat, without the hearts, notes or stars above) is as tall on screen as in the sharp V
# drawings (the 'scale' each one gets in coda_anchors.json).
import numpy as np, json
from PIL import Image
from scipy import ndimage
SHEETS = [('S', 'sheet_hug_hd3.webp', 2), ('T', 'sheet_hug_hd4.webp', 2), ('U', ['hug_hd_single1.webp', 'hug_hd_single2.webp', 'hug_hd_single3.webp', 'hug_hd_single4.webp', 'hug_hd_single5.webp'], 1),
          ('R', 'sheet_hug_hd5.webp', 2), ('K', 'sheet_hug_hd6.webp', 2),
          ('M', 'sheet_hug_hd7.webp', 2), ('N', 'sheet_hug_hd8.webp', 2)]
Z = dict(np.load('coda_sprites.npz').items()); A = json.load(open('coda_anchors.json'))
def card(rgb, al):   # the White Key Piano's cream card: its centre x and height
    cream = (al > 0.9) & (rgb[:, :, 0] > 0.8) & (rgb[:, :, 1] > 0.65) & (rgb[:, :, 2] > 0.55)
    lb, nb = ndimage.label(cream); big = np.argmax(ndimage.sum(cream, lb, range(1, nb + 1))) + 1
    ys, xs = np.nonzero(lb == big); return (xs.min() + xs.max()) / 2, ys.max() - ys.min() + 1
def group_h(al):   # the height of the biggest piece: the three characters, without what floats above them
    lb, nb = ndimage.label(al > 0.3, structure=np.ones((3, 3))); big = np.argmax(ndimage.sum(al > 0.3, lb, range(1, nb + 1))) + 1
    ys = np.nonzero(lb == big)[0]; return ys.max() - ys.min() + 1
REF = np.mean([group_h(Z[f'V_{i}_a'].astype(np.float32) / 255) for i in range(1, 5)]) * 260 / 171 * 0.893   # on screen in the V drawings
def cut(a, m, k):
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = max(0, ys.min() - 6), ys.max() + 7, max(0, xs.min() - 6), xs.max() + 7
    t = a[y0:y1, x0:x1].copy(); rgb = t[:, :, :3]; al = np.where(m[y0:y1, x0:x1], t[:, :, 3], 0)
    gx, _ = card(rgb, al); ch = group_h(al)
    Z[k + '_rgb'] = (rgb * 255 + 0.5).astype(np.uint8); Z[k + '_a'] = (al * 255 + 0.5).astype(np.uint8)
    A[k] = {'gx': float(gx), 'gy': int(np.nonzero((al > 0.5).any(1))[0].max()), 'bodyH': 0, 'bodyW': 0,
            'w': int(t.shape[1]), 'h': int(t.shape[0]), 'scale': float(REF / ch)}
    print(k, t.shape[1], t.shape[0], 'card centre', round(gx), 'scale', round(REF / ch, 3))
for name, path, grid in SHEETS:
    for j, p in enumerate(path if isinstance(path, list) else [path]):
        a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255
        H, W = a.shape[:2]; al = a[:, :, 3].copy(); al[al < 0.04] = 0
        lab, n = ndimage.label(al > 0.04, structure=np.ones((3, 3)))
        if grid == 1: cut(a, lab > 0, f'{name}_{j + 1}'); continue
        cms = ndimage.center_of_mass(al > 0.04, lab, range(1, n + 1))
        cell = np.array([-1] + [min(1, int(cy // (H / 2))) * 2 + min(1, int(cx // (W / 2))) for cy, cx in cms])
        cl = cell[lab]; cl[lab == 0] = -1
        for c in range(4): cut(a, cl == c, f'{name}_{c + 1}')
np.savez_compressed('coda_sprites.npz', **Z); json.dump(A, open('coda_anchors.json', 'w'), indent=0)
