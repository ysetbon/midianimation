# Part III of the étude (74.34 s to its last long chord at 100.11 s, held to 102.55 s): the white character, out of the piano, celebrating
# on petrol: cheering, bouncing to the groove, swaying through the soft passage, spinning,
# jumping on the peak and winding down. Poses change on the notes.
# Placement is automatic, as before: every pose's whole outline stays right of LEFT
# and left of a limit that follows the notes (the nearest visible note in the coming
# AHEAD seconds, minus GAP). Where the notes leave too little room for him at full
# size, the camera pulls back smoothly (starting early enough) and comes back in.
# Usage: partII.py source.mp4 out.mkv|mp4 [start_s end_s]    env: BG=hex, LOSSLESS=1
#        partII.py --still t out.png
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../coda')
from crop import cut_at   # the vanish line widens toward the end, before the Coda
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, CUT, FEATHER = 384, 480, 24
LEFT, GAP, AHEAD, GROUND = 35, 190, 1.1, 960
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
BG = hexc(os.environ.get('BG', '1f4a5c'))
Z = dict(np.load(D + '/partIII_sprites.npz').items()); ANCH = json.load(open(D + '/partIII_anchors.json'))
NL = json.load(open(D + '/notes_partIII.json'))['noteLeft']
# full size: his body as tall as at the end of the crossing (the chase sheet's last pose, drawn
# there at 475/256), measured on the arms-crossed pose both sheets share
bh = sorted(v['bodyH'] for v in ANCH.values())
FULL = 346 / bh[len(bh) // 2]   # his cream body as tall as in part I
# ---- the exposure sheet: (time, pose, body centre x, height above the ground, mirrored, may leave the frame)
def P(t, k, x=250, y=0, fl=0, ex=0): return (t, k, x, y, fl, ex)
_START = [P(96.17, 'H_1'), P(96.43, 'H_2'), P(96.56, 'H_3'), P(96.71, 'H_4'), P(96.96, 'H_6', y=70)]
_END = [P(99.06, 'H_12', y=90), P(99.19, 'H_13'), P(99.45, 'H_14'), P(100.11, 'H_15', 215, ex=1)]   # the bow: straight to his Coda spot (left edge 35 px) and still
FINALE_1 = _START + [P(97.23, 'H_7'), P(97.35, 'H_8'), P(97.63, 'H_5'), P(97.76, 'H_9'), P(98.01, 'H_1', fl=1),
                     P(98.27, 'H_10'), P(98.52, 'H_6', y=80), P(98.79, 'H_11')] + _END
FINALE_2 = _START + [P(97.23, 'H_7'), P(97.63, 'H_5'), P(98.01, 'H_10'), P(98.52, 'H_6', y=80), P(98.79, 'H_11'),
                     P(99.06, 'H_12', y=90), P(99.45, 'H_13'), P(100.11, 'H_15')]
SHEET = [
    # cheering: he has just burst out of the piano (74.3-78.6 s, loud joyful chords)
    P(74.30, 'E_1'), P(74.48, 'E_5'), P(74.87, 'E_3', y=60), P(75.14, 'E_4'), P(75.39, 'E_2', y=80), P(75.66, 'E_5'),
    P(75.78, 'E_6'), P(76.18, 'E_7'), P(76.44, 'E_8'), P(76.70, 'E_9'), P(77.10, 'E_13'), P(77.35, 'E_11'),
    P(77.62, 'E_12'), P(77.90, 'E_14'), P(78.15, 'E_10'), P(78.60, 'E_16'),
    # bouncing to the groove (78.85-83.4 s)
    P(78.85, 'G_1'), P(79.12, 'G_2'), P(79.37, 'G_4'), P(79.62, 'G_6'), P(79.80, 'G_8'), P(80.13, 'G_10'),
    P(80.40, 'G_3', y=50), P(80.66, 'G_7', y=50), P(80.93, 'G_5'), P(81.08, 'G_9'), P(81.44, 'G_2'), P(81.58, 'G_6', fl=1),
    P(81.85, 'G_11'), P(82.13, 'G_13'), P(82.41, 'G_14'), P(82.56, 'G_15'), P(82.83, 'G_16'), P(82.96, 'G_12'),
    # the soft, high passage: calm and swaying (83.4-85.4 s)
    P(83.43, 'F_2'), P(83.88, 'F_4'), P(84.26, 'F_8'), P(84.66, 'F_6'), P(85.04, 'F_16'),
    # climbing again: a little walk, a spin, clapping above his head (85.45-91.6 s)
    P(85.45, 'F_5', y=30), P(85.71, 'F_1', 235), P(85.97, 'F_3', 250), P(86.23, 'F_1', 262), P(86.49, 'F_3', 272),
    P(86.78, 'F_7', 272), P(87.16, 'F_9', 268), P(87.44, 'F_10', 266), P(87.71, 'F_11', 264), P(87.96, 'F_12', 262),
    P(88.23, 'F_10', 265), P(88.49, 'F_11', 260), P(88.75, 'F_12', 255), P(89.02, 'F_13'), P(89.16, 'F_14'), P(89.56, 'F_13'),
    P(89.82, 'F_14'), P(90.07, 'F_15', y=30), P(90.21, 'F_14'), P(90.47, 'F_15', y=30), P(90.72, 'F_7'), P(90.98, 'F_9'),
    P(91.26, 'F_15', y=30),
    # the peak: big jumps on the loudest chords (91.64-94.0 s)
    P(91.64, 'E_2', y=90), P(92.02, 'E_2', y=150), P(92.30, 'E_4'), P(92.55, 'E_5'), P(92.81, 'E_3', y=70), P(93.07, 'E_4'),
    P(93.34, 'E_6'), P(93.73, 'E_2', y=100), P(93.99, 'E_4'),
    # winding down toward the next crossing (94.25-96.17 s)
    P(94.25, 'G_13'), P(94.63, 'G_14'), P(94.90, 'G_15'), P(95.16, 'G_16'), P(95.42, 'G_11'), P(95.67, 'G_10'), P(95.92, 'G_9'),
    # the finale on the loud last run of chords: the ta-da lands on the loudest chord (99.06 s), and the long
    # chord before the Coda (100.11-102.55 s) is the bow alone. FINALE=2 uses fewer frames from 97 s on.
] + (FINALE_1 if os.environ.get('FINALE', '1') == '1' else FINALE_2)
def at(t):
    cur, nxt = SHEET[0], SHEET[1][0]
    for i, e in enumerate(SHEET):
        if e[0] <= t + 1e-6: cur, nxt = e, (SHEET[i + 1][0] if i + 1 < len(SHEET) else t + 0.4)
        else: break
    return cur, nxt
def visible_left(f):   # notes are cut at the vanish line, so none shows left of it
    v = NL[f] if 0 <= f < len(NL) else None
    return None if v is None else max(v, CUT)
# where the long bass notes pin him against the left limit (part II video 0:12-0:14), he may
# sit at 43 px from the frame's edge (chosen by eye)
LEFT_STRETCHES = []
# part II video 0:13 (46.35-47.65 s): centred exactly between the frame's left edge and the line where notes vanish
CENTRE_STRETCHES = []   # (from, to, nudge in px); the sitting pose at 0:14 sits 5 px left of centre
def left_limit(t):
    for a, b, v in LEFT_STRETCHES:
        if a <= t + 1e-6 < b: return v
    return LEFT
def right_limit(t0, t1):
    vals = [visible_left(f) for f in range(int(t0 * FPS), int((t1 + AHEAD) * FPS) + 2)]
    vals = [v for v in vals if v is not None]
    return min(W, (min(vals) if vals else W) - GAP)
# ---- the camera: full size unless the room left by the notes is too narrow for him
NEED = 400                                    # px of width he needs at full size (most poses are 300-400)
def _camera():
    n = len(NL); room = np.full(n, float(W))
    for f in range(n):
        room[f] = right_limit(f / FPS, f / FPS) - LEFT
    want = np.minimum(1.0, room / NEED)
    # look ahead and behind 0.6 s so it pulls back before the notes arrive, then ease it
    k = int(0.6 * FPS); lo = np.array([want[max(0, i - k):i + k + 1].min() for i in range(n)])
    w = int(0.5 * FPS); ker = np.ones(2 * w + 1) / (2 * w + 1)
    sm = np.convolve(np.pad(lo, w, mode='edge'), ker, mode='valid')
    return np.minimum(sm, lo + 0.02)          # never bigger than what fits
# NOSHRINK=1: always full size. Notes vanish at CUT, and he never reaches past it, so they can't touch him;
# where they come close the gap to the notes simply gets smaller than GAP for a moment
ZOOM = np.ones(len(NL))   # always full size: he never reaches past the vanish line
def cam_scale(t): return FULL * float(ZOOM[min(len(ZOOM) - 1, int(round(t * FPS)))])
sys.path.insert(0, D + '/../chase')
from chase import resize, paste, shadow, YY, XX   # shared helpers
_sprite = {}
def sprite(k, flip, s, air):
    key = (k, flip, round(s, 4), air)
    if key in _sprite: return _sprite[key]
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    an = ANCH[k]; gx, gy = an['gx'], an['gy']
    rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
    r = (resize(rgb, s), resize(a, s)[:, :, 0], gx * s, gy * s, an['bodyW'] * s)
    if len(_sprite) > 48: _sprite.clear()
    _sprite[key] = r
    return r
PLACED = []
def place(t):
    e, t1 = at(t); _, k, x, yoff, fl, ex = e
    s = cam_scale(t)
    rgb, a, gx, gy, bw = sprite(k, fl, s, yoff > 0)
    ox = round(x - gx)
    oy = round(GROUND - gy - yoff * s / FULL)
    cols = np.nonzero(a.max(0) > 0.05)[0]
    rlim = right_limit(e[0], t1)
    for a0, b0, dx in CENTRE_STRETCHES:
        if a0 <= e[0] + 1e-6 < b0: ox = round((CUT - (cols.max() - cols.min())) / 2 - cols.min()) + dx; ex = 1
    if not ex:
        if ox + cols.max() > rlim: ox -= ox + cols.max() - rlim
        if ox + cols.min() < left_limit(e[0]): ox += left_limit(e[0]) - (ox + cols.min())
    PLACED.append((round(t, 3), k, ox + int(cols.min()), ox + int(cols.max()), rlim, round(s / FULL, 3)))
    return rgb, a, ox, oy, yoff, bw
# the shine as he appears on part III's first two chords (74.34, 74.48): (time, level) keys for the light
# behind him and the flash in front of him, by option; the piano vanishes inside the first one
C1, C2 = 74.34, 74.48
SHINES = {
    'A': dict(halo=[(C1, .8), (74.45, .35), (C2, .75), (74.73, 0)], flash=[(C1, .85), (74.43, 0), (C2, .4), (74.56, 0)], r=(520, 360)),
    'B': dict(halo=[(C1, .9), (74.45, .5), (C2, .9), (74.87, 0)], flash=[], r=(560, 400)),
    'C': dict(halo=[(C1, 1.), (74.45, .55), (C2, .95), (74.87, 0)], flash=[(C1, 1.), (74.44, .15), (C2, .75), (74.62, .05), (74.87, 0)], r=(820, 560)),
}
SHINE = SHINES.get(os.environ.get('SHINE', 'B'))
LIGHT = np.array([1.0, 0.86, 0.95], np.float32)
def level(keys, t):
    if not keys or t < keys[0][0] or t >= keys[-1][0]: return 0.0
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t < t1: return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return 0.0
def light(img, lv, cx, cy, rx, ry):
    g = np.exp(-(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2))[:, :, None] * lv
    return img * (1 - g) + LIGHT * g
def frame(t, notes_rgb=None):
    img = np.broadcast_to(BG, (H, W, 3)).copy()
    rgb, a, ox, oy, yoff, bw = place(t)
    if SHINE:
        cx, cy = ox + a.shape[1] / 2, oy + a.shape[0] / 2; rx, ry = SHINE['r']
        if level(SHINE['halo'], t) > 0.01: img = light(img, level(SHINE['halo'], t), cx, cy, rx, ry)
    shadow(img, ox + a.shape[1] / 2, bw * 1.1, 0.30 * max(0.3, 1 - yoff / 300))
    paste(img, rgb, a, ox, oy)
    if notes_rgb is not None:
        v = np.clip((notes_rgb.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
        v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
        m = v.max(2, keepdims=True); na = np.clip((m - 0.02) / 0.98, 0, 1) * np.clip((np.arange(W, dtype=np.float32) - cut_at(t)) / FEATHER, 0, 1)[None, :, None]
        img = img * (1 - na) + np.where(m > 0, v / np.maximum(m, 1e-4), 0) * na
    if SHINE and level(SHINE['flash'], t) > 0.01: img = light(img, level(SHINE['flash'], t), cx, cy, rx * 0.65, ry * 0.75)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
def grab(src, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t - 0.5 / FPS:.4f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
SRC = os.environ.get('SRC', D + '/../etude1_final_v3.mp4')
def work(args):
    i, buf, f0 = args
    return frame((f0 + i) / FPS, np.frombuffer(buf, np.uint8).reshape(H, W, 3)).tobytes()
if __name__ == '__main__':
    if sys.argv[1] == '--still':
        from PIL import Image
        t = float(sys.argv[2]); Image.fromarray(frame(t, grab(SRC, t))).save(sys.argv[3]); sys.exit()
    src, dst = sys.argv[1:3]
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (2231 / FPS, 3077 / FPS)
    f0, f1 = round(t0 * FPS), round(t1 * FPS); n = f1 - f0
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    if os.environ.get('LOSSLESS'): venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    else: venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{f0 / FPS:.4f}', '-t', f'{n / FPS:.4f}', '-i', src, '-map', '0:v', '-map', '1:a', *venc, '-c:a', 'aac', '-b:a', '192k', dst], stdin=subprocess.PIPE)
    def frames():
        for i in range(n):
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b, f0
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=4): enc.stdin.write(out)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst, n, 'frames')
