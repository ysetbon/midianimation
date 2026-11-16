# Keeps a character the same size from pose to pose and sheet to sheet. The image tool draws some poses
# smaller in their cells; each pose is measured by rulers that only shrink when the character tilts or
# turns (never grow), and scaled so they match a reference size on screen.
import numpy as np
from scipy import ndimage
def _widest(m):
    lab, n = ndimage.label(m)
    if n == 0: return 0
    big = np.argmax(ndimage.sum(m, lab, range(1, n + 1))) + 1; xs = np.nonzero(lab == big)[1]
    return xs.max() - xs.min()
def black_key(rgb, a):            # the Black Key Piano: cap width, body width
    rgb = rgb.astype(float) / 255; a = a.astype(float) / 255
    navy = (a > 0.9) & (rgb.max(2) < 0.22) & (rgb[:, :, 2] > rgb[:, :, 0])
    pink = (a > 0.9) & (rgb[:, :, 0] > 0.85) & (rgb[:, :, 1] > 0.6) & (rgb[:, :, 1] < 0.85) & (rgb[:, :, 2] > 0.55) & (rgb[:, :, 2] < 0.8)
    return _widest(pink), _widest(navy)
def piano_front(rgb, a):          # the Brown Piano: width of its walnut front
    rgb = rgb.astype(float) / 255; a = a.astype(float) / 255
    wood = (a > 0.9) & (rgb[:, :, 0] > rgb[:, :, 1] + 0.08) & (rgb[:, :, 1] > rgb[:, :, 2]) & (rgb[:, :, 0] > 0.3) & (rgb.max(2) < 0.55)
    return _widest(wood)
CAP, BODY = 260.0, 184.0          # the Black Key Piano at 100% (end of the I -> II crossing), px on screen
def black_key_fix(Z, keys, scale, turned=()):
    fix = {}
    for k in keys:
        c, b = black_key(Z[k + '_rgb'], Z[k + '_a'])
        rc, rb = c * scale / CAP, b * scale / BODY
        est = max(rc, rb) if rb <= 1.12 else rc
        fix[k] = float(np.clip(1 / max(est, 1e-3), 0.85, 1.4))
    usual = float(np.median([v for k, v in fix.items() if k not in turned]))
    for k in turned: fix[k] = usual
    return fix, usual
