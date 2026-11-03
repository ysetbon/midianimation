# Part I's white key in the colours of the I -> II chase's first frame (chase W_1): each colour area of the
# drawing (cream face, lilac side edge, orange cheeks, the light rim of the card) is shifted, in Lab, so its
# median lands on the target; its shading (the spread inside the area) and everything black stays as it is.
import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation
TARGET = {'cream': '#fbdebb', 'lilac': '#9e9bfa', 'cheeks': '#fc9a47', 'rim': '#fcf8e7'}   # measured from chase W_1
def _lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def _gam(c): return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); WP = np.array([0.95047, 1.0, 1.08883])
def to_lab(rgb):
    xyz = _lin(rgb) @ M.T / WP; f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def to_rgb(lab):
    fy = (lab[..., 0] + 16) / 116; f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], -1)
    xyz = np.where(f > 0.2069, f ** 3, (f - 16 / 116) / 7.787) * WP
    return np.clip(_gam(xyz @ np.linalg.inv(M).T), 0, 1)
def hexlab(h): return to_lab(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) / 255)
def areas(rgb, al):
    mx, mn = rgb.max(-1), rgb.min(-1); v = mx; s = (mx - mn) / np.maximum(mx, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360
    op = al > 0.5
    lilac = op & (h > 220) & (h < 285) & (s > 0.2) & (v > 0.5)
    cheeks = op & (h > 8) & (h < 40) & (s > 0.55) & (v > 0.8)
    cream = op & (h > 15) & (h < 55) & (s > 0.12) & (s <= 0.55) & (v > 0.85)
    rim = op & (s <= 0.12) & (v > 0.9) & binary_dilation(cream, iterations=8)     # the light rim next to the face (not the motion lines)
    return {'cream': cream, 'lilac': lilac, 'cheeks': cheeks, 'rim': rim}
def apply(rgb, al, sigma=1.2):
    lab = to_lab(rgb); A = areas(rgb, al); dark = rgb.max(-1) < 0.35
    acc = np.zeros_like(lab); wsum = np.zeros(lab.shape[:2])
    for k, m in A.items():
        if m.sum() < 30: continue
        d = hexlab(TARGET[k]) - np.median(lab[m], 0)
        w = gaussian_filter(m.astype(float), sigma); w[dark] = 0
        acc += w[..., None] * d; wsum += w
    lab = lab + acc / np.maximum(wsum, 1)[..., None]
    return to_rgb(lab)
def report(rgb, al):
    lab = to_lab(rgb); out = {}
    for k, m in areas(rgb, al).items():
        if m.sum() > 30: c = np.median(rgb[m], 0); out[k] = '#%02x%02x%02x' % tuple((c * 255 + 0.5).astype(int))
    return out
