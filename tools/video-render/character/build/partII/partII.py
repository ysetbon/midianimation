# Part II of the étude (33.13-66.46 s): the black character alone on cocoa umber,
# fuming, throwing a tantrum, sulking and scheming, then leaping at the high notes
# until he runs out of steam. Poses change on the notes.
# Placement is automatic, as before: every pose's whole outline stays right of LEFT
# and left of a limit that follows the notes (the nearest visible note in the coming
# AHEAD seconds, minus GAP). Where the notes leave too little room for him at full
# size, the camera pulls back smoothly (starting early enough) and comes back in.
# Usage: partII.py source.mp4 out.mkv|mp4 [start_s end_s]    env: BG=hex, LOSSLESS=1
#        partII.py --still t out.png
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, CUT, FEATHER = 384, 480, 24
LEFT, GAP, AHEAD, GROUND = 35, 190, 1.1, 960
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
BG = hexc(os.environ.get('BG', '6e4a3c'))
Z = dict(np.load(D + '/partII_sprites.npz').items()); ANCH = json.load(open(D + '/partII_anchors.json'))
NL = json.load(open(D + '/notes_partII.json'))['noteLeft']
# full size: his body as tall as at the end of the crossing (the chase sheet's last pose, drawn
# there at 475/256), measured on the arms-crossed pose both sheets share
KA = json.load(open(os.environ.get('CHASE_ANCHORS', D + '/../chase/chase_anchors.json')))
FULL = (475 / 256) * KA['K_16']['bodyH'] / ANCH['A_1']['bodyH']
# ---- the exposure sheet: (time, pose, body centre x, height above the ground, mirrored, may leave the frame)
def P(t, k, x=250, y=0, fl=0, ex=0): return (t, k, x, y, fl, ex)
SHEET = [
    # II-1 fuming
    P(33.10, 'A_1'), P(33.41, 'A_2'), P(33.53, 'A_3'), P(33.67, 'A_5'), P(33.93, 'A_6'),
    P(34.09, 'A_4'), P(34.61, 'A_2'), P(34.73, 'A_3'), P(34.86, 'A_2'), P(34.97, 'A_3'),
    P(35.12, 'A_7'), P(35.29, 'A_6'), P(35.66, 'A_16'),
    P(36.05, 'A_8'), P(36.19, 'A_9'), P(36.32, 'A_10', y=70), P(36.44, 'A_11'), P(37.06, 'A_12'),
    P(37.24, 'A_11'), P(37.33, 'A_10', y=60), P(37.50, 'A_11'), P(37.62, 'A_12'), P(37.88, 'A_14'),
    P(38.16, 'A_13'), P(38.54, 'A_14'), P(38.81, 'A_5'), P(39.08, 'A_13'), P(39.33, 'A_6'),
    P(39.84, 'A_14'), P(40.10, 'A_15'), P(40.36, 'A_16'),
    # II-2 tantrum, the loudest stretch
    P(40.61, 'B_1'), P(41.02, 'B_2'), P(41.27, 'B_3', y=80), P(41.41, 'B_4'), P(41.55, 'B_3', y=60),
    P(41.79, 'B_5'), P(42.04, 'B_6'), P(42.17, 'B_7'), P(42.31, 'B_6'), P(42.44, 'B_7'), P(42.57, 'B_6'),
    P(42.69, 'B_7'), P(42.82, 'B_8'), P(42.96, 'B_9'), P(43.21, 'B_10'), P(43.34, 'B_11'),
    P(43.47, 'B_10'), P(43.59, 'B_11'), P(43.72, 'B_10'), P(43.85, 'B_11'), P(43.99, 'B_12'),
    P(44.24, 'B_13'), P(44.38, 'B_14', y=20), P(44.52, 'B_14'), P(44.65, 'B_12'), P(44.79, 'B_6'),
    P(44.92, 'B_7'), P(45.05, 'B_6'), P(45.17, 'B_7'), P(45.30, 'B_3', y=60), P(45.43, 'B_4'),
    P(45.56, 'B_5'), P(45.82, 'B_15'), P(46.35, 'B_16'),
    # II-3 sulking, then scheming and marching (back and forth, mirrored on the way back)
    P(46.60, 'C_1'), P(47.12, 'C_2'), P(47.66, 'C_3'), P(48.31, 'C_4'), P(48.57, 'C_3'), P(48.83, 'C_4'),
    P(49.10, 'C_5'), P(49.88, 'C_6'), P(50.29, 'C_7'), P(50.44, 'C_8'), P(50.86, 'C_7'), P(51.12, 'C_8'),
    P(51.24, 'C_9', 240), P(51.50, 'C_10', 255), P(51.75, 'C_11', 270), P(52.01, 'C_12', 285),
    P(52.28, 'C_9', 280, fl=1), P(52.54, 'C_10', 265, fl=1), P(52.79, 'C_11', 250, fl=1), P(53.05, 'C_12', 235, fl=1),
    P(53.32, 'C_13'), P(53.57, 'C_14'), P(53.97, 'C_15'), P(54.48, 'C_13', fl=1), P(54.75, 'C_14', fl=1),
    P(55.01, 'C_15'), P(55.67, 'C_16'),
    # II-4 leaping at the rising high notes, then out of steam
    P(56.04, 'D_1'), P(56.70, 'D_2', y=40), P(56.96, 'D_3'), P(57.10, 'D_1'), P(57.49, 'D_4', y=90),
    P(57.75, 'D_4', y=110), P(57.98, 'D_3'), P(58.12, 'D_1'), P(58.64, 'D_4', y=120), P(58.88, 'D_5', y=170),
    P(59.01, 'D_5', y=200), P(59.13, 'D_5', y=220), P(59.26, 'D_5', y=240), P(59.39, 'D_5', y=230),
    P(59.53, 'D_6', y=120), P(59.67, 'D_6', y=40), P(59.77, 'D_7'), P(60.45, 'D_8'), P(61.08, 'D_9'),
    P(61.49, 'D_10'), P(62.02, 'D_11'), P(62.70, 'D_12'), P(63.07, 'D_13'), P(63.40, 'D_12'),
    P(63.77, 'D_14'), P(64.43, 'D_15'), P(64.79, 'D_14'), P(65.31, 'D_15'), P(65.69, 'D_14'),
    P(66.11, 'D_15'), P(66.36, 'D_16')]
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
LEFT_STRETCHES = [(44.9, 45.82, 43), (45.82, 46.35, 38)]   # the steam blast at 0:46 sits 5 px further left
# part II video 0:13 (46.35-47.65 s): centred exactly between the frame's left edge and the line where notes vanish
CENTRE_STRETCHES = [(46.35, 46.6, -5), (46.6, 47.1, 0), (47.1, 47.65, -5)]   # (from, to, nudge in px); the freeze at 0:46 and the sitting pose at 0:47 sit 5 px left of centre
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
ZOOM = np.ones(len(NL)) if os.environ.get('NOSHRINK') else _camera()
def cam_scale(t): return FULL * float(ZOOM[min(len(ZOOM) - 1, int(round(t * FPS)))])
sys.path.insert(0, D + '/../chase')
from chase import resize, paste, shadow, YY, XX   # shared helpers
_sprite = {}
# every pose drawn the same size as at the end of the crossing: the image tool drew some poses smaller in
# their cells, so each pose is measured by its cap and its body width (both only get smaller when he tilts or
# turns, never bigger) and scaled up to match (cap 260 px, body 184 px wide on screen)
from scipy import ndimage as _nd
def _measure(k):
    rgb = Z[k + '_rgb'].astype(float) / 255; a = Z[k + '_a'].astype(float) / 255
    navy = (a > 0.9) & (rgb.max(2) < 0.22) & (rgb[:, :, 2] > rgb[:, :, 0])
    pink = (a > 0.9) & (rgb[:, :, 0] > 0.85) & (rgb[:, :, 1] > 0.6) & (rgb[:, :, 1] < 0.85) & (rgb[:, :, 2] > 0.55) & (rgb[:, :, 2] < 0.8)
    w = []
    for m in (pink, navy):
        lab, n = _nd.label(m)
        if n == 0: w.append(0); continue
        big = np.argmax(_nd.sum(m, lab, range(1, n + 1))) + 1; xs = np.nonzero(lab == big)[1]; w.append(xs.max() - xs.min())
    return w
CAP_REF, BODY_REF = 260.0, 184.0
POSE_FIX = {}
for _k in ANCH:
    _cw, _bw = _measure(_k)
    _rc, _rb = _cw * FULL / CAP_REF, _bw * FULL / BODY_REF
    _est = max(_rc, _rb) if _rb <= 1.12 else _rc            # a leaning body looks wider: trust the cap then
    POSE_FIX[_k] = float(np.clip(1 / max(_est, 1e-3), 1.0, 1.4))
# turned or tumbling poses only look narrower: they take their sheet's usual correction
for _k in ('B_10', 'B_11', 'D_6'):
    POSE_FIX[_k] = float(np.median([v for kk, v in POSE_FIX.items() if kk[0] == _k[0] and kk not in ('B_10', 'B_11', 'D_6')]))
def sprite(k, flip, s, air):
    s = s * POSE_FIX.get(k, 1.0)
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
sys.path.insert(0, D)
from recolor import notes_layer   # the hands' note colours (env NOTES)
def frame(t, notes_rgb=None):
    img = np.broadcast_to(BG, (H, W, 3)).copy()
    rgb, a, ox, oy, yoff, bw = place(t)
    shadow(img, ox + a.shape[1] / 2, bw * 1.1, 0.30 * max(0.3, 1 - yoff / 300))
    paste(img, rgb, a, ox, oy)
    if notes_rgb is not None:
        v = np.clip((notes_rgb.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
        v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
        col, al = notes_layer(v)
        na = np.clip((al[..., None] - 0.02) / 0.98, 0, 1) * np.clip((np.arange(W, dtype=np.float32) - CUT) / FEATHER, 0, 1)[None, :, None]
        img = img * (1 - na) + col * na
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
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (994 / FPS, 1994 / FPS)
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
