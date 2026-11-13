# The black key's colours on the sleeping frames (2026-11-03): each colour area (pink cap and limbs, green stripe,
# band and cheeks, the black body, the dark gloves and shoes) is shifted in Lab so its median lands on the frames
# just before and after (Z4 and Z9, averaged), keeping its own shading; outlines, eyes, "z" and bubble stay.
# usage: recolor_black.py in.png out.png [ref_sheet:cell ...]   (as hd/recolor.py does for the white key)
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../hd'); from recolor import to_lab, to_rgb
def areas(rgb, a):
    v = rgb.max(-1); mx, mn = v, rgb.min(-1); s = (mx - mn) / np.maximum(mx, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]; h = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360; op = a > 0.5
    return {'pink': op & ((h < 35) | (h > 340)) & (s > 0.15) & (s < 0.6) & (v > 0.75),
            'green': op & (h > 90) & (h < 170) & (s > 0.25) & (v > 0.35),
            'body': op & (v > 0.02) & (v < 0.13) & (h > 140) & (h < 220),
            'gloves': op & (v > 0.08) & (v < 0.3) & ((h < 60) | (h > 330))}
def medians(rgb, a): return {k: np.median(to_lab(rgb[m]), 0) for k, m in areas(rgb, a).items() if m.sum() > 50}
def apply(rgb, a, target, sigma=1.2):
    lab = to_lab(rgb); acc = np.zeros_like(lab); wsum = np.zeros(lab.shape[:2])
    for k, m in areas(rgb, a).items():
        if m.sum() < 50 or k not in target: continue
        d = target[k] - np.median(lab[m], 0); w = gaussian_filter(m.astype(float), sigma)
        w[rgb.max(-1) < 0.02] = 0   # the black outlines stay black
        acc += w[..., None] * d; wsum += w
    return to_rgb(lab + acc / np.maximum(wsum, 1)[..., None])
CELL = {'tl': (0, 0), 'tr': (768, 0), 'bl': (0, 512), 'br': (768, 512)}
def cell(path, c):
    sh = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32) / 255; x, y = CELL[c]; return sh[y:y + 512, x:x + 768]
if __name__ == '__main__':
    src, dst, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
    meds = [medians(c[..., :3], c[..., 3]) for c in (cell(*r.split(':')) for r in refs)]
    target = {k: np.mean([m[k] for m in meds if k in m], 0) for k in meds[0]}
    sh = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32) / 255; out = sh.copy()
    for c, (x, y) in CELL.items():
        part = sh[y:y + 512, x:x + 768]; out[y:y + 512, x:x + 768, :3] = apply(part[..., :3], part[..., 3], target)
    Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(dst)
    for c in CELL:
        part = out[CELL[c][1]:CELL[c][1] + 512, CELL[c][0]:CELL[c][0] + 768]; m = medians(part[..., :3], part[..., 3])
        print(c, {k: '#%02x%02x%02x' % tuple((to_rgb(v[None])[0] * 255 + 0.5).astype(int)) for k, v in m.items()})
    print('target', {k: '#%02x%02x%02x' % tuple((to_rgb(v[None])[0] * 255 + 0.5).astype(int)) for k, v in target.items()})
