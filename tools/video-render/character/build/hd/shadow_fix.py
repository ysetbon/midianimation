# Part I's drawings carry their own ground shadow (a soft dark oval). ChatGPT redrew it as opaque grey with a light
# rim, uneven from frame to frame; here it is replaced by a clean oval drawn at full resolution, with the same
# place, size, darkness and soft edge as the old drawing's shadow.
import numpy as np
from scipy.ndimage import label
def oval(rgb, a):
    """the old shadow: centre, radii, darkness, edge softness (old pixels), or None"""
    rgb = rgb.astype(float) / 255; a = a.astype(float) / 255; h, w = a.shape
    M = (rgb.max(-1) < 0.15) & (a > 0.03) & (a < 0.8)          # see-through dark: the shadow (feet are opaque)
    lab, n = label(M); keep = []
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lab == j)
        if len(ys) >= 150 and ys.max() >= 0.6 * h and (xs.max() - xs.min()) > 2.5 * (ys.max() - ys.min() + 1) * 0.6: keep.append(j)
    if not keep: return None
    m = np.isin(lab, keep)
    rows = m.sum(1); wide = np.nonzero(rows > 0.35 * rows.max())[0]           # the oval's rows, not the feet's thin edges
    y0, y1 = wide.min(), wide.max()
    band = m[y0:y1 + 1]; xs = np.nonzero(band.any(0))[0]
    cy = (y0 + y1) / 2; ry = (y1 - y0 + 1) / 2 + 1.5; cx = (xs.min() + xs.max()) / 2; rx = (xs.max() - xs.min() + 1) / 2 + 1.5
    core = m & (np.abs(np.arange(h)[:, None] - cy) < ry * 0.5)
    A0 = float(np.median(a[core])) if core.sum() > 20 else float(np.median(a[m]))
    return dict(cx=cx, cy=cy, rx=rx, ry=ry, A0=A0, soft=2.5)
def draw(sh, H, W, F):
    """the oval's alpha on a canvas F x the old size"""
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    x = (xs + 0.5) / F - 0.5 - sh['cx']; y = (ys + 0.5) / F - 0.5 - sh['cy']
    r = np.sqrt((x / sh['rx']) ** 2 + (y / sh['ry']) ** 2) + 1e-6
    g = np.sqrt((x / sh['rx'] ** 2) ** 2 + (y / sh['ry'] ** 2) ** 2) / r + 1e-6      # |grad r|, so the soft edge is even all round
    d = (r - 1) / g                                                                  # distance outside the oval, old pixels
    return (sh['A0'] * np.clip(0.5 - d / (2 * sh['soft']), 0, 1)).astype(np.float32)
def replace(rgb, al, sh, F):
    """take the redraw's own shadow out (the wide grey patch near the bottom, and the light rim around it) and put
    the clean oval under the drawing"""
    from scipy.ndimage import binary_dilation
    H, W = al.shape; s = draw(sh, H, W, F)
    L = rgb.mean(-1); sat = rgb.max(-1) - rgb.min(-1); neutral = sat < 0.12
    G = neutral & (L > 0.15) & (L < 0.9) & (al > 0.3)
    lab, n = label(G); keep = np.zeros_like(G)
    x0, x1 = (sh['cx'] - sh['rx']) * F, (sh['cx'] + sh['rx']) * F
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lab == j)
        if len(ys) < 400 or ys.max() < 0.55 * H: continue                      # small bits, or too high up
        if (xs.max() - xs.min()) < 2 * (ys.max() - ys.min() + 1): continue     # not wide and flat
        if xs.max() < x0 or xs.min() > x1: continue                             # not under the character
        keep |= lab == j
    ring = binary_dilation(keep, iterations=4 * F)
    out = keep | (ring & neutral & (L > 0.13) & (al < 0.95))                   # the patch, and its soft light rim
    ac = np.where(out, 0, al)
    a = ac + s * (1 - ac)
    rgb = np.where(a[..., None] > 1e-4, rgb * ac[..., None] / np.maximum(a[..., None], 1e-4), 0)
    return np.clip(rgb, 0, 1), np.clip(a, 0, 1)
