# The II -> III crossing (66.47-74.34 s) and the first seconds of part III: a piano falls
# from the sky onto the black character on the crossing's biggest chord (71.83 s), lies
# there wrecked while the chord rings, starts to glow and bursts open on part III's first
# beat (74.34 s). His legs stick out from under it, twitching.
# Usage: t2.py source.mp4 out.mkv [start_s end_s]   env: LOSSLESS=1, BG=hex
#        t2.py --still t out.png
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D + '/../chase')
from chase import resize, paste, shadow, YY, XX
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, CUT, FEATHER = 384, 480, 24
LEFT, GAP, AHEAD, GROUND = 35, 190, 1.1, 960
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
BG = hexc(os.environ.get('BG', '6e4a3c')); BG3 = hexc(os.environ.get('BG3', '1f4a5c'))   # part II's cocoa umber; part III's petrol
Z = dict(np.load(D + '/t2_sprites.npz').items()); ANCH = json.load(open(D + '/t2_anchors.json'))
NL = json.load(open(D + '/notes_t2.json'))['noteLeft']
K16 = json.load(open(D + '/../chase/chase_anchors.json'))['K_16']['bodyH']
S_SCALE = 1.855 * K16 / ANCH['S_1']['bodyH']                         # his body as tall as in part II
SCALE = {'S': S_SCALE, 'U': S_SCALE * ANCH['S_1']['bodyH'] / ANCH['U_1']['bodyH'],
         'L': S_SCALE * 103 / 329, 'R': S_SCALE * 103 / 329,         # legs: his shoes the same size as on the sheet
         'P': 1.35}                                                   # the piano: clearly bigger than him
sys.path.insert(0, D + '/../chase')
import sizefix
FIX, _usual = sizefix.black_key_fix(Z, [f'S_{i}' for i in range(1, 17)], SCALE['S'], turned=('S_4', 'S_5', 'S_6', 'S_7', 'S_8', 'S_9'))
_c, _b = sizefix.black_key(Z['U_1_rgb'], Z['U_1_a'])                      # looking up: cap tilted, body turned; take the mean
FIX['U_1'] = 1 / ((_c * SCALE['U'] / sizefix.CAP + _b * SCALE['U'] / sizefix.BODY) / 2)
FIX_LEGS = _usual
_fall = sorted(sizefix.piano_front(Z[f'P_{i}_rgb'], Z[f'P_{i}_a']) for i in (1, 2, 3, 5, 6, 7, 8, 9))
SCALE['P'] = 379.0 / _fall[len(_fall) // 2]                               # the Brown Piano at 100%: front 379 px, as tall as in the Coda's hug
CX = 250                                                              # where he stands
PX = 290                                                              # where the piano lands (covering him)
# ---- him: (time, pose, mirrored)
BLACK = [(66.40, 'S_1', 0), (67.14, 'S_15', 0), (67.80, 'S_1', 0), (68.18, 'S_15', 0), (68.70, 'S_1', 0),
         (69.23, 'S_15', 0), (69.63, 'U_1', 0),                       # big chord: he looks up (a whistle, a shadow)
         (70.03, 'S_3', 0), (70.32, 'S_3', 1), (70.48, 'S_3', 0), (70.64, 'S_3', 1),   # panic
         (70.83, 'S_4', 0), (71.83, None, 0)]                         # ducks; then only his legs are left
LEGS = [(71.83, 1), (72.60, 2), (73.45, 1), (74.00, None)]   # they twitch as the piano changes frame
# ---- the piano: (time, pose)
# it starts falling at 70.0 s (1:10), lands on the biggest chord, wrecks, glows and bursts; the burst's
# flash hides it and his legs, and has faded exactly as the long chord ends and part III begins
PIANO = [(70.00, 'P_1'), (70.48, 'P_2'), (71.19, 'P_3'),                     # falling
         (71.83, 'P_4'), (72.10, 'P_6'), (72.60, 'P_7'), (73.45, 'P_10'), (73.85, 'P_13'), (74.00, None)]   # impact, crack, dizzy wreck, glow, burst
FALL = (70.00, 71.83)
# SHINE (A/B/C): no light during the long chord; the piano's burst frame stays until part III's first chord,
# where it vanishes in the shine around the White Key Piano (drawn in partIII.py). Empty: the light on the long chord.
SHINE = os.environ.get('SHINE', 'B')
if SHINE:
    PIANO = PIANO[:-1]; LEGS = LEGS[:-1]
# PFRAME (1/2/3): the piano's frames after landing, timed so it is gone on the frame before part III's first notes reach it
PFRAMES = {
    '1': (290, [(71.83, 'P_4'), (72.10, 'P_6'), (72.45, 'P_7'), (72.85, 'P_10'), (73.15, 'P_12'), (73.40, 'P_13'), (73.59, None)]),   # bursts early, then an empty stage
    '2': (290, [(71.83, 'P_4'), (72.10, 'P_6'), (72.60, 'P_7'), (73.15, 'P_10'), (73.50, 'P_12'), (73.85, None)]),                    # no burst: leaves in its light beam
    '3': (113, [(71.83, 'P_4'), (72.10, 'P_6'), (72.60, 'P_7'), (73.45, 'P_10'), (73.75, 'P_12'), (74.00, 'P_13'), (74.19, None)]),   # lands further left, bursts just before part III
}
# PFRAME 4/5/6: the vanish line slides right before the long chord's notes come near (no notes are left of it
# then, so the slide is unseen), so they are eaten before the piano's swirl; the piano stays to the chord's end
# with one more frame, and vanishes as the White Key Piano appears (74.34)
_BASE = [(71.83, 'P_4'), (72.10, 'P_6'), (72.60, 'P_7'), (73.15, 'P_10'), (73.50, 'P_12')]
PFRAMES.update({'4': (290, _BASE + [(73.95, 'P_13')]), '5': (290, _BASE + [(73.95, 'P_11')]), '6': (290, _BASE + [(73.95, 'P_15')])})
PCROP = {'4': 765, '5': 700, '6': 700}.get(os.environ.get('PFRAME', '5'), CUT)
CROP_SLIDE = (72.4, 72.9)
def cut_at(t): return CUT + (PCROP - CUT) * ease((t - CROP_SLIDE[0]) / (CROP_SLIDE[1] - CROP_SLIDE[0]))
if os.environ.get('PFRAME', '5') in PFRAMES:
    PX, _after = PFRAMES[os.environ.get('PFRAME', '5')]
    PIANO = PIANO[:3] + _after
    if _after[-1][1] is None: _gone = _after[-1][0]; LEGS = [l for l in LEGS if l[0] < _gone] + [(_gone, None)]
BURST, GONE, III = 73.85, 74.00, 74.34   # burst, piano and legs gone in the flash, flash gone as part III's first chord sounds
def at(sheet, t):
    cur = None
    for e in sheet:
        if e[0] <= t + 1e-6: cur = e
        else: break
    return cur
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
_sprite = {}
def sprite(k, flip=0):
    key = (k, flip)
    if key in _sprite: return _sprite[key]
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    an = ANCH[k]; gx, gy = an['gx'], an['gy']; s = SCALE[k[0]] * FIX.get(k, FIX_LEGS if k[0] in 'LR' else 1.0)
    if k[0] != 'P': rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
    r = (resize(rgb, s), resize(a, s)[:, :, 0], gx * s, gy * s)
    _sprite[key] = r
    return r
def burst_level(t):   # how strong the light around the piano is
    if SHINE or t < 71.83 or t >= III: return 0.0
    if t < 73.45: return 0.45 * np.exp(-(t - 71.83) / 0.5) + 0.12   # the landing's burst settling to a faint glow
    if t < GONE: return 0.12 + 0.6 * ease((t - 73.45) / (GONE - 73.45))   # swelling as it glows and opens
    return 0.72 * (1 - ease((t - GONE) / (III - GONE)))                   # fading out, gone exactly at part III
LIGHT = np.array([1.0, 0.86, 0.95], np.float32)
def light(img, level, core=False):   # a soft round light around the piano, not the whole screen
    rx, ry = (330, 260) if core else (520, 360)
    g = np.exp(-(((XX - PX) / rx) ** 2 + ((YY - 820) / ry) ** 2))[:, :, None] * level
    return img * (1 - g) + LIGHT * g
# the white one, out of the burst (his part III sheet, at part III's size)
Z3 = dict(np.load(D + '/../partIII/partIII_sprites.npz').items()); A3 = json.load(open(D + '/../partIII/partIII_anchors.json'))
_bh = sorted(v['bodyH'] for v in A3.values()); S3 = 346 / _bh[len(_bh) // 2]
RISE = []   # the White Key Piano appears with part III's first chord (74.34 s), not before
_white = {}
def white(k):
    if k not in _white:
        rgb = Z3[k + '_rgb'].astype(np.float32) / 255; a = Z3[k + '_a'].astype(np.float32) / 255
        rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)
        _white[k] = (resize(rgb, S3), resize(a, S3)[:, :, 0], A3[k]['gx'] * S3, A3[k]['gy'] * S3)
    return _white[k]
def right_limit(t0, t1):
    vals = [max(v, CUT) for v in NL[int(t0 * FPS):int((t1 + AHEAD) * FPS) + 2] if v is not None]
    return min(W, (min(vals) if vals else W) - GAP)
sys.path.insert(0, D + '/../partII')
from recolor import notes_layer
def frame(t, notes_rgb=None):
    img = np.broadcast_to(BG, (H, W, 3)).copy()
    # part III's colour spreads out from the crash while the chord rings, complete as the piano bursts open
    if t >= GONE: img = np.broadcast_to(BG3, (H, W, 3)).copy()
    elif t >= 71.83:
        u = (t - 71.83) / (GONE - 71.83); r = 120 + 2300 * (u ** 1.5)
        d = np.sqrt((XX - PX) ** 2 + ((YY - 900) * 1.15) ** 2)
        m = np.clip((r - d) / 420 + 0.5, 0, 1); m = m * m * (3 - 2 * m)
        m = np.clip(m + (np.random.default_rng(int(t * FPS)).random((H, W), np.float32) - 0.5) * (8 * m * (1 - m)) * 0.02, 0, 1)[:, :, None]
        img = BG * (1 - m) + BG3 * m
    # the piano's shadow grows under him from the moment he hears the whistle
    if 69.63 <= t < 71.83:
        u = (t - 69.63) / (71.83 - 69.63); shadow(img, PX, 60 + 360 * u * u, 0.12 + 0.4 * u)
    # the glow from inside the piano, and the burst on part III's first beat
    if 71.83 <= t < III:   # the light behind the piano: from the landing, swelling as it opens, gone exactly at part III
        img = light(img, burst_level(t) * 0.75)
    e = at(BLACK, t)
    if e and e[1]:
        rgb, a, gx, gy = sprite(e[1], e[2]); ox, oy = round(CX - gx), round(GROUND - gy)
        cols = np.nonzero(a.max(0) > 0.05)[0]
        if ox + cols.max() > right_limit(e[0], e[0] + 0.4): ox -= ox + cols.max() - right_limit(e[0], e[0] + 0.4)
        if ox + cols.min() < LEFT: ox += LEFT - (ox + cols.min())
        if e[1] != 'U_1': shadow(img, ox + a.shape[1] / 2, 260, 0.25)
        paste(img, rgb, a, ox, oy)
    l = at(LEGS, t)
    if l and l[1]:   # flat legs sticking out on both sides; their inner ends hide under the piano
        for side, x_out in (('L', 0), ('R', PX + 330)):
            rgb, a, gx, gy = sprite(f'{side}L_{l[1]}'); oy = round(GROUND - gy) + 6
            ox = x_out if side == 'L' else x_out - a.shape[1]
            paste(img, rgb, a, ox, oy)
    p = at(PIANO, t)
    if p and p[1]:
        rgb, a, gx, gy = sprite(p[1])
        lift = 0.0
        if t < FALL[1]:   # already peeking in at the top at 70.0 s, then faster and faster, moving in 0.2 s steps like his other frames
            ts = FALL[0] + int((t - FALL[0]) / 0.2 + 1e-6) * 0.2; u = (ts - FALL[0]) / (FALL[1] - FALL[0]); lift = (GROUND - 220) * (1 - u ** 1.8)
        if p[1] == 'P_5': lift = 40
        ox, oy = round(PX - gx), round(GROUND - gy - lift)
        if t >= FALL[1]: shadow(img, PX, a.shape[1] * 0.9, 0.35)
        paste(img, rgb, a, ox, oy)
    w = at(RISE, t)
    if w and t < III:   # the white one pops up out of the burst, landing as part III begins
        rgb, a3, gx, gy = white(w[1]); paste(img, rgb, a3, round(PX - 20 - gx), round(GROUND - gy - w[2]))
    if notes_rgb is not None:
        v = np.clip((notes_rgb.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
        v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
        col, al = notes_layer(v)   # part II's last notes in the hands' new colours
        na = np.clip((al[..., None] - 0.02) / 0.98, 0, 1) * np.clip((np.arange(W, dtype=np.float32) - cut_at(t)) / FEATHER, 0, 1)[None, :, None]
        img = img * (1 - na) + col * na
    if not SHINE and 71.83 <= t < III:   # the flash in front: a burst on the landing, and again as the piano opens (it hides the piano and his legs as they go)
        f = 0.9 * np.exp(-(t - 71.83) / 0.18) if t < BURST else 0.0
        if BURST <= t < GONE: f = 0.95 * ease((t - BURST) / (GONE - BURST))
        elif t >= GONE: f = 0.95 * (1 - ease((t - GONE) / (III - GONE)))
        if f > 0.01: img = light(img, f, core=True)
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
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (1994 / FPS, 2290 / FPS)
    f0, f1 = round(t0 * FPS), round(t1 * FPS); n = f1 - f0
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', *venc, dst], stdin=subprocess.PIPE)
    def frames():
        for i in range(n):
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b, f0
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=4): enc.stdin.write(out)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst, n, 'frames')
