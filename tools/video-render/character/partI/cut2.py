# Cut the 48 poses from the transparent sprite sheets: tiles found between the
# white grid lines, frame numbers removed, faint paper haze dropped, the ground
# shadow made pure darkness (so it takes the colour of any background), and
# each pose anchored on its shadow.
import numpy as np, json, os
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
OLD = {17: 14, 18: 16, 19: 15}          # same poses as the navy sheets, same names
def runs(ix):
    r = []; s = p = None
    for k in ix:
        if s is None or k != p + 1:
            if s is not None: r.append((s, p))
            s = k
        p = k
    if s is not None: r.append((s, p))
    return r
out = {}; anchors = {}
for i, old in OLD.items():
    a = np.asarray(Image.open(f'{D}/../sheets/partI_{i}.png').convert('RGBA')).astype(np.float32) / 255
    line = (a[:, :, 3] > 0.8) & (a[:, :, :3].mean(2) > 0.85)
    cols = runs(np.where(line.mean(0) > 0.7)[0]); rows = runs(np.where(line.mean(1) > 0.7)[0])
    # keep 5 lines each way (merge near duplicates), add the outer edges when missing
    def five(r, n=1254):
        r = [x for x in r]
        if r[0][0] > 20: r.insert(0, (0, 0))
        if r[-1][1] < n - 20: r.append((n - 1, n - 1))
        return r
    cols, rows = five(cols), five(rows)
    assert len(cols) == 5 and len(rows) == 5, (i, cols, rows)
    for r in range(4):
        for c in range(4):
            t = a[rows[r][1] + 4:rows[r + 1][0] - 3, cols[c][1] + 4:cols[c + 1][0] - 3].copy()
            h, w = t.shape[:2]
            rgb, al = t[:, :, :3], t[:, :, 3]
            al[:int(h * 0.17), :int(w * 0.17)] = 0                     # frame number
            al[al < 0.1] = 0                                           # paper haze
            lum = rgb.mean(2); sat = rgb.max(2) - rgb.min(2)
            shadow = (lum < 0.45) & (sat < 0.08) & (al < 0.9)          # the grey ground shadow
            rgb[shadow] = 0
            haze = (lum > 0.9) & (sat < 0.05) & (al < 0.6)              # white fringe from the paper
            al[haze] *= 0.3
            ys, xs = np.nonzero(shadow[int(h * 0.6):])
            if len(ys) > 150: gy, gx, kind = int(np.median(ys)) + int(h * 0.6), int(np.median(xs)), 'shadow'
            else:
                ys, xs = np.nonzero(al > 0.5); gy = int(ys.max()); gx = int(np.median(xs[ys > ys.max() - 20])); kind = 'lowest'
            k = f'{old}_{r * 4 + c + 1}'
            out[k + '_rgb'] = (rgb * 255 + 0.5).astype(np.uint8); out[k + '_a'] = (al * 255 + 0.5).astype(np.uint8)
            anchors[k] = {'gx': gx, 'gy': gy, 'kind': kind, 'bg': [0, 0, 0]}
np.savez_compressed(D + '/sprites.npz', **out); json.dump(anchors, open(D + '/anchors.json', 'w'), indent=0)
print(len(anchors), 'poses;', sum(v['kind'] == 'shadow' for v in anchors.values()), 'anchored on their shadow')
