# The user's sharp redraws of the Black Key Piano's hands-on-cheeks pose B 10 (2026-11-01):
# BS_1 glancing sideways like B 10, BS_2 looking ahead (the one used at 1:57.4, the user's pick). Each is sized so his cap and body are
# as wide on screen as B 10's, and anchored on his body's centre and his lowest foot.
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage
os.environ.setdefault('TIMEMAP', '1:0')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
Z = dict(np.load('coda_sprites.npz').items()); A = json.load(open('coda_anchors.json'))
def widest(m):
    lab, n = ndimage.label(m); big = np.argmax(ndimage.sum(m, lab, range(1, n + 1))) + 1; xs = np.nonzero(lab == big)[1]
    return xs.min(), xs.max()
def measure(rgb, a):   # cap width, body width and body centre (the body is navy in the old sheets, pure black here)
    rgb = rgb.astype(float) / 255; a = a.astype(float) / 255
    body = (a > 0.9) & (rgb.max(2) < 0.22)
    pink = (a > 0.9) & (rgb[:, :, 0] > 0.85) & (rgb[:, :, 1] > 0.6) & (rgb[:, :, 1] < 0.85) & (rgb[:, :, 2] > 0.55) & (rgb[:, :, 2] < 0.8)
    c0, c1 = widest(pink); b0, b1 = widest(body)
    return c1 - c0, b1 - b0, (b0 + b1) / 2
import coda   # B 10's size on screen now
old_s = coda.SCALE['B'] * coda.BFIX['B_10']; oc, ob, _ = measure(Z['B_10_rgb'], Z['B_10_a'])
for k, f in (('BS_1', 'black_key_cheeks_side.webp'), ('BS_2', 'black_key_cheeks_front.webp')):
    a = np.asarray(Image.open(f).convert('RGBA')).astype(np.float32) / 255
    m = a[:, :, 3] > 0.04; ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = max(0, ys.min() - 6), ys.max() + 7, max(0, xs.min() - 6), xs.max() + 7
    t = a[y0:y1, x0:x1]; rgb = (t[:, :, :3] * 255 + 0.5).astype(np.uint8); al = (t[:, :, 3] * 255 + 0.5).astype(np.uint8)
    c, b, gx = measure(rgb, al)
    s = float(np.mean([oc * old_s / c, ob * old_s / b]))
    Z[k + '_rgb'] = rgb; Z[k + '_a'] = al
    A[k] = {'gx': float(gx), 'gy': int(np.nonzero((al > 128).any(1))[0].max()), 'bodyH': 0, 'bodyW': 0, 'w': int(t.shape[1]), 'h': int(t.shape[0]), 'scale': s}
    print(k, t.shape[1], t.shape[0], 'scale', round(s, 3), 'cap', round(c * s), 'vs', round(oc * old_s), 'body', round(b * s), 'vs', round(ob * old_s), 'height', round(t.shape[0] * s), 'vs', round(Z['B_10_a'].shape[0] * old_s))
np.savez_compressed('coda_sprites.npz', **Z); json.dump(A, open('coda_anchors.json', 'w'), indent=0)
