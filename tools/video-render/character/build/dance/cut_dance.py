# The white key's dance at 1:24-1:34.5 (2026-11-03): the user's four ChatGPT sheets in
# redraw/new_frames/dance_sheet01-04.png (2 x 2, 768 x 512 cells, D1-D16 in storyboard order) are cut into
# dance_sprites.npz, in the white key's exact colours (hd/recolor.py), with anchors: gx the card's centre, gy the
# lowest point (where he stands), bodyH and bodyW the card's size (its biggest light area, cream, rim and lilac).
# DS in dance_anchors.json scales them so he stands as tall as in his other part III frames (450 px, beret to feet).
import os, sys, json, numpy as np
from PIL import Image
from scipy import ndimage as nd
D = os.path.dirname(os.path.abspath(__file__)); RD = D + '/../../redraw/new_frames'
sys.path.insert(0, D + '/../hd'); import recolor
CW, CH = 768, 512
def card(rgb, a):
    light = (a > 0.5) & (rgb.max(-1) > 0.45)
    lab, n = nd.label(light); m = lab == (np.argmax(nd.sum(light, lab, range(1, n + 1))) + 1)
    ys, xs = np.nonzero(m); return m, ys, xs
def cut(sheet_glob_n, prefix, first):
    out, anch = {}, {}
    for s in range(sheet_glob_n):
        sheet = np.asarray(Image.open(f'{RD}/{first}0{s + 1}.png').convert('RGBA')).astype(np.float32) / 255
        for c in range(4):
            n = 4 * s + c + 1; cx, cy = c % 2, c // 2
            cell = sheet[cy * CH:(cy + 1) * CH, cx * CW:(cx + 1) * CW]; a = cell[..., 3]
            lab, k = nd.label(a > 0.04)   # the drawing and its extras; drop stray specks
            sizes = nd.sum(a > 0.04, lab, range(1, k + 1)); keep = np.isin(lab, 1 + np.nonzero(sizes >= 40)[0])
            a = np.where(nd.binary_dilation(keep, iterations=2), a, 0)
            ys, xs = np.nonzero(a > 0.04); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            rgb = cell[y0:y1, x0:x1, :3]; a = a[y0:y1, x0:x1]
            rgb = recolor.apply(rgb, a)
            m, cyy, cxx = card(rgb, a)
            solid = np.nonzero((a > 0.5).any(1))[0]
            out[f'{prefix}_{n}_rgb'] = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8); out[f'{prefix}_{n}_a'] = (a * 255 + 0.5).astype(np.uint8)
            anch[f'{prefix}_{n}'] = dict(gx=float(cxx.mean()), gy=float(solid.max() + 1), bodyH=float(cyy.max() - cyy.min() + 1),
                                         bodyW=float(cxx.max() - cxx.min() + 1), w=int(x1 - x0), h=int(y1 - y0), colours=recolor.report(rgb, a))
    return out, anch
if __name__ == '__main__':
    out, anch = cut(4, 'DN', 'dance_sheet')
    # standing with the beret on top (moonwalk, arm wave, tiptoes): as tall as he stands in part III, beret to
    # feet 450 px on screen (measured in the video at 1:23-1:36)
    upright = [f'DN_{i}' for i in (5, 6, 7, 13, 14)]
    anch['DS'] = 450.0 / float(np.median([anch[k]['h'] for k in upright]))
    np.savez_compressed(D + '/dance_sprites.npz', **out); json.dump(anch, open(D + '/dance_anchors.json', 'w'), indent=1)
    for k in sorted((k for k in anch if k != 'DS'), key=lambda k: int(k[3:])): print(k, {x: (round(v, 1) if isinstance(v, float) else v) for x, v in anch[k].items()})
    print('DS', round(anch['DS'], 3))
