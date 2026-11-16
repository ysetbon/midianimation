# Part II's notes in new colours. The source draws part II's right hand mint (top) and left hand blue (bottom);
# from about 1:04 its palette morphs note by note into part III's (right hand: mint -> pale azure -> lilac,
# left hand: blue -> periwinkle -> violet). Each hand's part II colour becomes its new colour, part III's
# colours stay, and the notes in between get the same blend, so the handover to part III stays smooth.
# The light tips and flashes are kept, and both hands are equally solid (the source blue was only 74% bright).
# NOTES=rrggbb,rrggbb (right hand, left hand); NOTES=none keeps the source colours.
import os, numpy as np
from scipy.ndimage import gaussian_filter
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
_n = os.environ.get('NOTES', 'e8916a,b81d2c')   # chosen: light rust (right hand) and deep red (left hand)
TARGETS = [hexc(c) for c in _n.split(',')] if _n and _n != 'none' else None
W0, M0 = (0.28, 0.08), (0.94, 0.74)   # whiteness and brightness of the plain source colours (right, left)
def _hue(c, mx, d):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return np.where(mx == r, ((g - b) / (d + 1e-6)) % 6, np.where(mx == g, (b - r) / (d + 1e-6) + 2, (r - g) / (d + 1e-6) + 4)) * 60
def _ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def notes_layer(v, targets=TARGETS):
    """v: the notes, 0..1 on black. Returns (colour, alpha)."""
    m = v.max(2); col = np.where(m[..., None] > 0, v / np.maximum(m, 1e-4)[..., None], 0); al = m.copy()
    mask = m > 0.02
    if not targets or not mask.any(): return col, al
    ys, xs = np.nonzero(mask); win = (slice(max(0, ys.min() - 4), ys.max() + 5), slice(max(0, xs.min() - 4), xs.max() + 5))
    mw, cw = m[win], col[win]
    wt = np.where(mw > 0.02, mw, 0)   # colour smoothed over each note (the video's colour noise, smeared edges)
    den = gaussian_filter(wt, 1.5) + 1e-6
    cb = np.stack([gaussian_filter(cw[..., k] * wt, 1.5) / den for k in range(3)], -1)
    mx, mn = cb.max(-1), cb.min(-1); d = mx - mn; wh = mn / (mx + 1e-6); h = _hue(cb, mx, d)
    other = (h < 95) & (1 - wh > 0.25)                       # part I's orange and yellow notes stay
    pR = np.where((h < 182) | (h >= 280), 1.0, 1 / (1 + np.exp(-(wh - 0.55) / 0.06)))[..., None]   # right hand: greener, or paler
    u = (pR * _ss((h - 170) / 130)[..., None] + (1 - pR) * _ss((h - 200) / 52)[..., None])          # 0 part II colour .. 1 part III colour
    T = pR * targets[0] + (1 - pR) * targets[1]
    w0 = pR * W0[0] + (1 - pR) * W0[1]; m0 = (pR * M0[0] + (1 - pR) * M0[1])[..., 0]
    wr = _ss((np.clip((wh[..., None] - w0) / (1 - w0), 0, 1) - 0.3) / 0.45)    # plain colour, or pale (tips, flashes)
    newc = T + (1 - T) * wr; newa = np.minimum(1, mw / m0)
    keep = other | (mw <= 0.02)
    col[win] = np.where(keep[..., None], cw, newc * (1 - u) + cw * u)
    al[win] = np.where(keep, mw, newa * (1 - u[..., 0]) + mw * u[..., 0])
    return col, al
