# How big each sleep frame is drawn (2026-11-13). cut_sleep.py sizes them all with one scale, ZS, so that the beret
# is 250 px wide on screen in the standing frames. Measured that way, the frames where the beret is tilted (lying
# asleep, Z_5-Z_9; waking, Z_10; scrambling up, Z_11) come out bigger than the standing ones, because a tilted
# beret is narrower across than it really is: in final 30 his beret is 236-251 px across standing and 273-279 px
# lying and waking. Here each frame instead gets the scale that makes the beret's true diameter (its long axis,
# whatever its tilt) 243 px on screen: halfway between the frame before the sleep (D_13, 236 px) and the one after
# the wake-up (S_1, 251 px), so both hand-overs are smooth.
# SLEEP_SIZE: 'width' (as before, the default until the user picks), 'diameter' (the full correction) or a number between 0 and 1 to go only part of the way.
import os, numpy as np
from scipy import ndimage as nd
def _diameter(rgb, a):   # the beret's long axis, in sheet pixels (rgb, a as floats 0..1)
    pink = (a > 0.9) & (rgb[..., 0] > 0.85) & (rgb[..., 1] > 0.6) & (rgb[..., 1] < 0.85) & (rgb[..., 2] > 0.55) & (rgb[..., 2] < 0.8)
    lab, n = nd.label(pink); cap = lab == (np.argmax(nd.sum(pink, lab, range(1, n + 1))) + 1)
    cap = nd.binary_fill_holes(nd.binary_closing(cap, iterations=4))
    ys, xs = np.nonzero(cap); ev = np.linalg.eigvalsh(np.cov(np.vstack([xs, ys]).astype(float)))
    return 4 * np.sqrt(ev.max()) * 0.866
_cache = {}
TARGET = 243.0   # px on screen
def factor(SL, k, ZS):
    """the size correction for sleep frame k, on top of ZS"""
    mode = os.environ.get('SLEEP_SIZE', 'width')
    if mode == 'width': return 1.0
    if not _cache:
        for kk in sorted({x[:-4] for x in SL.files if x.endswith('_rgb')}):
            _cache[kk] = _diameter(SL[kk + '_rgb'].astype(np.float32) / 255, SL[kk + '_a'].astype(np.float32) / 255)
    full = TARGET / (_cache[k] * ZS)
    part = 1.0 if mode == 'diameter' else float(mode)
    return 1 + (full - 1) * part
