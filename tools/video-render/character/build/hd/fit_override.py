# Fits a redrawn frame onto the canvas of an existing sharp drawing in hd_sprites.npz, as a drop-in replacement
# (2026-11-12: the user's ChatGPT fix of part II's A_4, arms crossed with both hands showing; redraw/A_4_fix/).
# The new drawing is recoloured to the old one's colours (each pixel is matched to the nearest fill colour, as a blend
# of that fill with the black outline, and given the old fill at the same strength), scaled so the figure is as tall
# as before, its feet on the same line and its body centred where the old body was. The result goes to
# hd/overrides/<part>_<key>.png, which hd.get() prefers over hd_sprites.npz (NOOVERRIDE=1 ignores the overrides).
# Usage: fit_override.py <part> <key> <new.png> <new fill hexes> <old fill hexes>   (comma-separated, in pairs)
import os, sys, numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
part, key, src, new_hex, old_hex = sys.argv[1:6]
hx = lambda s: np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in s.split(',')], np.float32) / 255
NEW, OLD = hx(new_hex), hx(old_hex)
H = np.load(D + '/hd_sprites.npz'); orgb = H[f'{part}:{key}_rgb'].astype(np.float32) / 255; oa = H[f'{part}:{key}_a'].astype(np.float32) / 255
im = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32) / 255; rgb, a = im[..., :3], im[..., 3]
# recolour: p ~ t * F_new (t in 0..1, 0 = the black outline); the best-fitting fill gives t * F_old
best = np.full(a.shape, 1e9, np.float32); out = rgb.copy()
for Fn, Fo in zip(NEW, OLD):
    t = np.clip((rgb @ Fn) / float(Fn @ Fn), 0, 1)
    err = np.linalg.norm(rgb - t[..., None] * Fn, axis=-1) + 0.25 * (1 - t)   # prefer a fill at full strength (a dark brown shoe is not pink faded into the outline)
    m = err < best; best = np.where(m, err, best); out = np.where(m[..., None], t[..., None] * Fo, out)
rgb = np.where((best < 0.12 + 0.25)[..., None], out, rgb)   # anything that matches no fill (eyes, mouth, glove lines) stays as drawn
def box(al):
    ys, xs = np.nonzero(al > 0.5); return ys.min(), ys.max(), xs.min(), xs.max()
def body_cx(r, al):   # the dark body's middle (outline and fill), a third of the way down the figure
    y0, y1, _, _ = box(al); yy = int(y0 + (y1 - y0) * 0.62)
    xs = np.nonzero((al[yy] > 0.5) & (r[yy].max(-1) < 0.25))[0]; return (xs.min() + xs.max()) / 2
ny0, ny1, _, _ = box(a); oy0, oy1, _, _ = box(oa)
s = (oy1 - oy0) / (ny1 - ny0)
pre = lambda m: Image.fromarray(m.astype(np.float32), 'F')
H2, W2 = round(a.shape[0] * s), round(a.shape[1] * s)
ra = np.asarray(pre(a).resize((W2, H2), Image.LANCZOS)); prgb = [np.asarray(pre(rgb[..., c] * a).resize((W2, H2), Image.LANCZOS)) for c in range(3)]
ra = np.clip(ra, 0, 1); rgb2 = np.clip(np.stack(prgb, -1) / np.maximum(ra[..., None], 1e-4), 0, 1) * (ra[..., None] > 1e-4)
dx = round(body_cx(orgb, oa) - body_cx(rgb2, ra)); dy = round(oy1 - box(ra)[1])
canvas = np.zeros((orgb.shape[0], orgb.shape[1], 4), np.float32)
ys, xs = np.mgrid[0:H2, 0:W2]; ty, tx = ys + dy, xs + dx; ok = (ty >= 0) & (ty < canvas.shape[0]) & (tx >= 0) & (tx < canvas.shape[1])
canvas[ty[ok], tx[ok], :3] = rgb2[ok]; canvas[ty[ok], tx[ok], 3] = ra[ok]
lost = ra[~ok].sum() / max(ra.sum(), 1)
Image.fromarray((canvas * 255 + 0.5).astype(np.uint8), 'RGBA').save(f'{D}/overrides/{part}_{key}.png')
print(f'{part}:{key}: scale {s:.3f}, moved {dx},{dy}; figure outside the old canvas: {lost * 100:.1f}%')
