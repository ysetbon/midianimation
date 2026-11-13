# The white key juggling flowers at 0:10.9-0:12.9 (2026-11-03): the user's two ChatGPT sheets in
# redraw/new_frames/juggle_sheet01-02.png (2 x 2, 768 x 512 cells, J1-J8 in storyboard order) are cut into
# juggle_sprites.npz in the white key's exact colours (hd/recolor.py, as ../dance/cut_dance.py does), each with
# part I's soft ground shadow drawn under its feet (as measured in the video: 328 x 42 px, 54% dark, soft edge).
# JS scales them so his cream face is 300 px tall on screen, as in part I; gx is the face's centre, feet his lowest
# point (it goes on part I's standing line there, the shoes' bottom at y 979 on screen, as in 14_5 just before).
import os, sys, json, numpy as np
from scipy import ndimage as nd
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D + '/../dance'); from cut_dance import cut
FACE_H, SH_RX, SH_RY, SH_A, SH_SOFT, SH_UP = 300.0, 164.0, 21.0, 0.54, 5.0, 14.0   # on screen (the shadow's centre 14 px above the shoes' bottom, as just before)
def face(rgb):
    t = np.array([0xfb, 0xde, 0xbb]) / 255; m = np.abs(rgb - t).max(-1) < 0.06
    lab, n = nd.label(m); big = lab == (np.argmax(nd.sum(m, lab, range(1, n + 1))) + 1); return np.nonzero(big)
out, anch = cut(2, 'J', 'juggle_sheet')
keys = [f'J_{i}' for i in range(1, 9)]
# 2026-11-12: the user's third ChatGPT redraw has the right outline and legs, but the card came out 12-18% too narrow
# (and the second sheet a little wider than the first). Each frame is stretched sideways so its card is as wide for its
# height as in his other part I poses (208 x 303 px on screen in 16_1 and 16_5). The card is measured a third of the
# way down (the eyes' height); J1 (the bouquet covers the card) and J8 (the tilted bow) can't be measured that way and
# take the median stretch of their own sheet. JUGGLE_WIDTH=0 leaves the drawings as they are.
CARD_WH = 208.0 / 303.0
def card_wh(k):
    rgb = out[k + '_rgb'].astype(float) / 255; a = out[k + '_a'].astype(float) / 255
    m = (np.abs(rgb - np.array([0xfb, 0xde, 0xbb]) / 255).max(-1) < 22 / 255) & (a > 0.8)
    lab, n = nd.label(m); big = lab == (np.argmax(nd.sum(m, lab, range(1, n + 1))) + 1)
    ys = np.nonzero(big)[0]; h = ys.max() - ys.min() + 1; row = np.nonzero(big[ys.min() + h // 3])[0]
    return (row.max() - row.min() + 1) / h
if os.environ.get('JUGGLE_WIDTH', '1') != '0':
    f = {k: CARD_WH / card_wh(k) for k in keys}
    for sheet in (keys[:4], keys[4:]):
        good = [f[k] for k in sheet if k not in ('J_1', 'J_8')]
        for k in sheet:
            if k in ('J_1', 'J_8'): f[k] = float(np.median(good))
    for k in keys:
        rgb = out[k + '_rgb'].astype(np.float32) / 255; a = out[k + '_a'].astype(np.float32) / 255
        pa = nd.zoom(a, (1, f[k]), order=1); prgb = nd.zoom(rgb * a[..., None], (1, f[k], 1), order=1)
        rgb = np.where(pa[..., None] > 1e-4, np.clip(prgb / np.maximum(pa[..., None], 1e-4), 0, 1), 0)
        out[k + '_rgb'] = (rgb * 255 + 0.5).astype(np.uint8); out[k + '_a'] = (np.clip(pa, 0, 1) * 255 + 0.5).astype(np.uint8)
        anch[k].update(w=int(pa.shape[1]), stretch=round(f[k], 3))
    print('stretched sideways:', {k: round(v, 3) for k, v in f.items()})
fh = {}
for k in keys:
    ys, xs = face(out[k + '_rgb'].astype(float) / 255); fh[k] = ys.max() - ys.min() + 1; anch[k]['gx'] = float(xs.mean())
JS = FACE_H / float(np.median(list(fh.values())))
for k in keys:   # the shadow under the feet, on a canvas widened to hold it
    rgb = out[k + '_rgb'].astype(np.float32) / 255; a = out[k + '_a'].astype(np.float32) / 255; h, w = a.shape
    feet = anch[k]['gy']; rx, ry, soft = SH_RX / JS, SH_RY / JS, SH_SOFT / JS; cx = anch[k]['gx']
    padl = int(max(0, rx + soft - cx)) + 2; padr = int(max(0, cx + rx + soft - w)) + 2; padb = int(max(0, feet + ry + soft - h)) + 2
    H2, W2 = h + padb, w + padl + padr
    rgb2 = np.zeros((H2, W2, 3), np.float32); a2 = np.zeros((H2, W2), np.float32)
    rgb2[:h, padl:padl + w] = rgb; a2[:h, padl:padl + w] = a
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
    r = np.sqrt(((xx - cx - padl) / rx) ** 2 + ((yy - feet + SH_UP / JS) / ry) ** 2)
    sa = SH_A * np.clip((1 - r) * min(rx, ry) / soft + 0.5, 0, 1)          # the oval, softened over its edge
    na = a2 + sa * (1 - a2)
    rgb2 = np.where(na[..., None] > 1e-4, rgb2 * a2[..., None] / np.maximum(na[..., None], 1e-4), 0)   # shadow is black
    out[k + '_rgb'] = (rgb2 * 255 + 0.5).astype(np.uint8); out[k + '_a'] = (np.clip(na, 0, 1) * 255 + 0.5).astype(np.uint8)
    anch[k].update(gx=cx + padl, feet=feet, face=float(fh[k]), w=W2, h=H2)
anch['JS'] = JS
np.savez_compressed(D + '/juggle_sprites.npz', **out); json.dump(anch, open(D + '/juggle_anchors.json', 'w'), indent=1)
for k in keys: print(k, {x: (round(v, 1) if isinstance(v, float) else v) for x, v in anch[k].items() if x != 'colours'}, anch[k]['colours'])
print('JS', round(JS, 3))
