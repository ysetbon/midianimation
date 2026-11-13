# The black key's tired-and-asleep frames at 1:09-1:13 (2026-11-03): the user's three ChatGPT sheets in
# redraw/new_frames/sleep_sheet01-03.png (2 x 2, 768 x 512 cells, Z1-Z12 in storyboard order) are cut into
# sleep_sprites.npz with anchors: gx the body's centre (its black), gy the lowest point (where he rests on the
# ground), bodyW the width of his black body (for the ground shadow), cap the width of his pink cap.
# ZS in sleep_anchors.json scales them so the cap is 250 px on screen, as in his frames around them.
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as nd
D = os.path.dirname(os.path.abspath(__file__)); RD = D + '/../../redraw/new_frames'
CW, CH = 768, 512
out, anch = {}, {}
for s in range(3):
    sheet = np.asarray(Image.open(f'{RD}/sleep_sheet0{s + 1}.png').convert('RGBA')).astype(np.float32) / 255
    for c in range(4):
        n = 4 * s + c + 1; cx, cy = c % 2, c // 2
        cell = sheet[cy * CH:(cy + 1) * CH, cx * CW:(cx + 1) * CW]
        a = cell[..., 3]
        lab, k = nd.label(a > 0.04)   # the drawing and its extras (z's, bubbles, marks); drop stray specks
        sizes = nd.sum(a > 0.04, lab, range(1, k + 1)); keep = np.isin(lab, 1 + np.nonzero(sizes >= 40)[0])
        keep = nd.binary_dilation(keep, iterations=2); a = np.where(keep, a, 0)
        ys, xs = np.nonzero(a > 0.04); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgb = cell[y0:y1, x0:x1, :3]; a = a[y0:y1, x0:x1]
        dark = (a > 0.9) & (rgb.max(-1) < 0.22)
        dl, dn = nd.label(dark); body = dl == (np.argmax(nd.sum(dark, dl, range(1, dn + 1))) + 1)
        bx = np.nonzero(body)[1]
        pink = (a > 0.9) & (rgb[..., 0] > 0.85) & (rgb[..., 1] > 0.6) & (rgb[..., 1] < 0.85) & (rgb[..., 2] > 0.55) & (rgb[..., 2] < 0.8)
        pl, pn = nd.label(pink); cap = pl == (np.argmax(nd.sum(pink, pl, range(1, pn + 1))) + 1); px = np.nonzero(cap)[1]
        solid = np.nonzero((a > 0.5).any(1))[0]
        # his body, gloves and shoes pure black, as in all his other frames (they were dark teal and brown, 2026-11-11)
        rgb = rgb * np.clip((rgb.max(-1, keepdims=True) - 0.22) / 0.08, 0, 1)
        out[f'Z_{n}_rgb'] = (rgb * 255 + 0.5).astype(np.uint8); out[f'Z_{n}_a'] = (a * 255 + 0.5).astype(np.uint8)
        anch[f'Z_{n}'] = dict(gx=float(bx.mean()), gy=float(solid.max() + 1), bodyW=float(bx.max() - bx.min()), cap=float(px.max() - px.min()),
                              w=int(x1 - x0), h=int(y1 - y0))
caps = [anch[k]['cap'] for k in ('Z_1', 'Z_2', 'Z_12')]   # standing: the cap seen straight on
CAP = 250.0   # his cap on screen at the end of part II and the start of the crossing (measured in the video, 1:10-1:13)
anch['ZS'] = CAP / float(np.median(caps))
np.savez_compressed(D + '/sleep_sprites.npz', **out); json.dump(anch, open(D + '/sleep_anchors.json', 'w'), indent=1)
for k in sorted((k for k in anch if k != 'ZS'), key=lambda k: int(k[2:])): print(k, {x: round(v, 1) for x, v in anch[k].items()})
print('ZS', round(anch['ZS'], 3))
