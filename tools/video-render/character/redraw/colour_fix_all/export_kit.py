# export_kit.py (2026-11-15): every Black Key drawing whose colours differ from Z_12 at 1:13, at the size it is stored,
# for the user's GPT pass (one zip). Run from build/ with the build env (TIMEMAP etc.). Writes the frames and
# frames.csv (each frame's group, when it is on screen, and its colours now) next to this script.
import os, sys, csv, json, numpy as np
from PIL import Image
from scipy import ndimage
K = os.path.dirname(os.path.abspath(__file__))
B = os.path.abspath(os.path.join(K, '..', '..', 'build')); sys.path.insert(0, B); sys.path.insert(0, B + '/hd'); sys.argv = ['x']
import hd as HD, timemap as TM
def save(rgb, a, path):
    rgb = np.asarray(rgb); a = np.asarray(a)
    if rgb.dtype != np.uint8: rgb = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    if a.dtype != np.uint8: a = (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, a]), 'RGBA').save(path)
def hx(c): return '#%02x%02x%02x' % tuple(int(round(v)) for v in c)
def colours(path):
    im = np.asarray(Image.open(path).convert('RGBA')).astype(float); P = im[..., :3]; a = im[..., 3] / 255
    R, G, Bc = P[..., 0], P[..., 1], P[..., 2]; op = a > 0.9
    pink = op & (R > 200) & (G > 120) & (Bc > 110) & (R - Bc > 35) & (R - G > 40)
    lab, n = ndimage.label(pink); out = {'strip': '', 'beret': '', 'beret line': '', 'body': ''}
    if not n: return out
    ber = lab == (np.argmax(ndimage.sum(pink, lab, range(1, n + 1))) + 1); ys, xs = np.nonzero(ber); bw = xs.max() - xs.min()
    reg = np.zeros(a.shape, bool); reg[ys.min():ys.max() + int(1.6 * bw), max(0, xs.min() - bw // 3):xs.max() + bw // 3] = True
    green = reg & op & (G > R + 15) & (G > Bc)
    out['beret'] = hx(np.median(P[ber], 0))
    lab2, n2 = ndimage.label(green)
    if n2:
        strip = lab2 == (np.argmax(ndimage.sum(green, lab2, range(1, n2 + 1))) + 1)
        line = green & ndimage.binary_dilation(ber, iterations=6) & (~strip | (np.roll(ber, 6, 0) & np.roll(ber, -6, 0)))
        if strip.sum() > 30: out['strip'] = hx(np.median(P[strip], 0))
        if line.sum() > 15: out['beret line'] = hx(np.median(P[line & (G > np.percentile(G[line], 25))], 0))
    body = reg & op & (P.max(2) < 70); body &= ~ndimage.binary_dilation(~op, iterations=6)   # inside, away from the outline
    if body.sum() > 100: out['body'] = hx(np.median(P[body], 0))
    return out
rows = []
def add(group, key, rgb, a, times, note=''):
    d = os.path.join(K, group); os.makedirs(d, exist_ok=True); p = os.path.join(d, f'{key}.png'); save(rgb, a, p)
    c = colours(p); rows.append([group, f'{key}.png', ', '.join(f'{int(t // 60)}:{t % 60:05.2f}' for t in times[:4]) + (' ...' if len(times) > 4 else ''),
                                 c['strip'], c['beret'], c['beret line'], c['body'], note])
# 1: after the sleep, the beret line only (the user's recoloured frames as they are in final 36)
T2 = {'S_1': [74.23, 75.21], 'S_15': [74.64, 75.79], 'U_1': [76.23], 'S_3': [76.67, 76.99, 77.16, 77.34], 'S_4': [77.55]}
for k, ts in T2.items():
    im = np.asarray(Image.open(os.path.join(B, 'hd', 'overrides', 't2_colour', k + '.png')).convert('RGBA'))
    add('1_after_the_sleep', k, im[..., :3], im[..., 3], ts, 'only the beret line is off')
# 2: the crossing I -> II (chase.py's K_1-K_16)
sys.path.insert(0, B + '/chase'); import chase as C
seen = {}
for e in C.BLACK:
    if e[1]: seen.setdefault(e[1], []).append(TM.new(e[0]))
for i in sorted(seen):
    r = HD.get('chase', f'K_{i}'); add('2_crossing', f'K_{i}', r[0], r[1], seen[i])
# 3: part II (partII.py's A_1-D_13)
sys.path.insert(0, B + '/partII'); import partII as P2
seen = {}
for e in P2.SHEET:
    if not e[1].startswith('Z'): seen.setdefault(e[1], []).append(TM.new(e[0]))
for k in sorted(seen, key=lambda k: (k[0], int(k[2:]))):
    r = HD.get('partII', k); add('3_part_II', k, r[0], r[1], seen[k])
# 4 and 5: the coda (the fall, and the hugs with both characters)
sys.path.insert(0, B + '/coda'); cwd = os.getcwd(); os.chdir(B + '/coda'); import coda as CO; os.chdir(cwd)
CZ = dict(np.load(B + '/coda/coda_sprites.npz').items())
def coda_img(k):
    r = HD.get('coda', k)
    return (r[0], r[1]) if r is not None else (CZ[k + '_rgb'], CZ[k + '_a'])
seen = {}
for e in CO.BLACK:
    if e[1]: seen.setdefault(e[1], []).append(TM.new(e[0]))
for k, ts in seen.items(): add('4_coda_fall', k, *coda_img(k), ts)
seen = {}
for e in CO.HUG:
    if e[1]: seen.setdefault(e[1], []).append(TM.new(e[0]))
for k, ts in seen.items(): add('5_coda_hugs', k, *coda_img(k), ts, 'both characters: recolour only the Black Key')
with open(os.path.join(K, 'frames.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['folder', 'file', 'on screen at', 'green strip now', 'beret now', 'beret line now', 'body now', 'note']); w.writerows(rows)
print(len(rows), 'frames')
