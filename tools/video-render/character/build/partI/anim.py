# Part I of the étude: the cut-out character animated at 5 poses a second on
# the empty navy background, timed to the music, with the notes on top
# (moved so they are hit at 50% of the width and gone at 25%).
# Usage: anim.py video out.mp4 [seconds]
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hd')); import hd as HD   # the sharp redraws (hd/make_hd.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
import timemap as TM   # choreography time <-> video time (TIMEMAP)
src, dst = sys.argv[1:3]
DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 26.217
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
import os
SHIFT, CUT, FEATHER = int(os.environ.get('SHIFT', 192)), 480, 24   # the render hits notes at 40% of the width; SHIFT moves them right
SCALE, GROUND, HOME = float(os.environ.get('SCALE', 2.05)), 960, 240
MARGIN = 24   # every pose stays this far inside the frame's left edge and short of the line where notes vanish
LEFTLIM = int(os.environ.get('LEFTLIM', MARGIN)); RIGHTLIM = int(os.environ.get('RIGHTLIM', 480 - MARGIN))   # the character's own limits, in px
D = __file__.rsplit('/', 1)[0]
A, B, C = 16, 14, 15   # the three sheets: warming up, burst and rest, shimmer
# exposure sheet: (from second, sheet, pose, anchor x in px, mirrored)
X = HOME
# every entry lands on a note of ethude_1_27 (2026-11-11, the timing review): the poses used to change on a 0.2 s grid,
# up to 0.15 s away from the notes; the drawings and their order are the same, one step of the walk back (8.2) is gone,
# and the walk at the end steps on every eighth note. (10.4-11.8 are only shown with NOJUGGLE=1.)
SHEET = [
    (0.0, A, 1), (0.56, A, 2), (0.82, A, 1), (1.21, A, 2), (1.34, A, 3), (1.87, A, 4), (2.26, A, 5),
    (2.79, A, 6), (3.05, A, 5), (3.32, A, 7), (3.57, A, 8), (3.83, A, 9), (4.22, A, 10), (4.35, A, 11),
    (5.40, A, 12, 252), (5.54, A, 13, 260), (5.80, A, 12, 268), (6.06, A, 13, 275), (6.34, A, 12, 282),
    (6.47, A, 13, 282), (6.74, A, 14, 276, 1), (6.86, A, 15, 270, 1), (7.11, A, 16, 264, 1),
    (7.38, A, 15, 258, 1), (7.64, A, 14, 252, 1), (7.90, A, 15, 249, 1), (8.03, A, 16, 244, 1),
    (8.29, A, 1), (8.55, B, 1), (8.71, B, 2), (8.96, B, 3), (9.23, B, 2), (9.36, B, 1), (9.61, B, 4),
    (10.25, B, 5), (10.4, B, 6), (10.6, B, 7), (10.8, B, 6), (11.0, B, 7), (11.2, B, 8), (11.6, B, 9), (11.8, B, 8),
    (12.35, B, 10), (12.60, B, 11), (12.86, B, 12), (13.12, B, 13), (13.39, B, 12),
    (13.65, B, 11), (14.04, B, 16), (14.17, B, 14), (14.56, B, 12), (14.84, B, 13), (14.97, B, 15),
    (16.03, B, 16), (16.18, B, 15), (16.82, C, 1), (17.20, C, 2), (17.46, C, 3), (17.59, C, 2),
    (17.83, C, 3), (17.99, C, 2), (18.25, C, 3), (18.39, C, 4), (18.78, C, 5), (19.42, C, 6),
    (19.81, C, 7), (20.75, C, 8), (21.16, C, 9), (21.68, C, 10),
] + [(22.84 + 0.2608 * k, C, 11 + k % 4, 243 + 4 * k) for k in range(10)] + [
    (25.43, C, 15, 280), (25.70, C, 16, 280), (25.95, C, 15, 280)]
# 0:10.9-0:12.9 (the user's flower juggling, 2026-11-03; ../juggle/cut_juggle.py) instead of the spiral-eyed dizzy
# frames: a toss on each falling A, the big toss on the first loud chord (12.07), the catch on the second (12.21),
# a shy bow, then he sits down with 14_10 at 12.35 (0:13.66)
if not os.environ.get('NOJUGGLE'):
    SHEET = [e for e in SHEET if not 10.39 < e[0] < 12.19] + [
        (10.40, 'J', 1), (10.54, 'J', 2), (10.66, 'J', 3), (10.91, 'J', 4), (11.05, 'J', 5), (11.19, 'J', 4),
        (11.32, 'J', 5), (11.45, 'J', 6), (11.58, 'J', 7), (11.97, 'J', 8)]
    SHEET.sort(key=lambda e: e[0])
SHEET = [(e[0], e[1], e[2], e[3] if len(e) > 3 else X, e[4] if len(e) > 4 else 0) for e in SHEET]
# the sitting poses reach further left from their shadow: sit a little to the right
SIT = {(B, p) for p in range(10, 17)} | {(C, 1)}
SHEET = [(t, sh, po, x + 45 if (sh, po) in SIT else x, fl) for t, sh, po, x, fl in SHEET]
def pose_at(t):
    cur = SHEET[0]
    for e in SHEET:
        if e[0] <= t + 1e-6: cur = e
        else: break
    return cur
SP = os.environ.get('SPRITES', D)          # folder of cut-out poses (the transparent sheets live in ../sprites2)
CLEAN = SP != D                             # those have no navy in their edges to take out
Z = dict(np.load(SP + '/sprites.npz').items()); ANCH = json.load(open(SP + '/anchors.json'))
def resize_j(m, SC):
    m = m if m.ndim == 3 else m[:, :, None]; h, w = m.shape[:2]; nh, nw = round(h * SC), round(w * SC)
    ys = np.clip((np.arange(nh) + 0.5) / SC - 0.5, 0, h - 1); xs = np.clip((np.arange(nw) + 0.5) / SC - 0.5, 0, w - 1)
    y0 = ys.astype(int); x0 = xs.astype(int); y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    return (m[y0][:, x0] * (1 - fx) + m[y0][:, x1] * fx) * (1 - fy) + (m[y1][:, x0] * (1 - fx) + m[y1][:, x1] * fx) * fy
JZ = dict(np.load(D + '/../juggle/juggle_sprites.npz').items()); JA = json.load(open(D + '/../juggle/juggle_anchors.json'))
FEET_J = 979   # the juggling frames' shoes stand where 14_5's do, just before them
def scaled(sheet, pose, flip):
    k = f'{sheet}_{pose}'
    if sheet == 'J':   # the flower juggling (../juggle/cut_juggle.py): own sheet, face 300 px tall, shadow drawn in
        rgb = JZ[k + '_rgb'].astype(np.float32) / 255; a = JZ[k + '_a'].astype(np.float32) / 255; an = JA[k]; s = JA['JS']
        gx = an['gx']
        if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
        pa = resize_j(a, s)
        return np.where(pa > 1e-4, np.clip(resize_j(rgb * a[:, :, None], s) / np.maximum(pa, 1e-4), 0, 1), 0), pa, gx * s, an['feet'] * s - (FEET_J - GROUND)
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    w0 = a.shape[1]; F = 1   # the sharp redraw, if there is one: F x the old size, same anchors
    _h = HD.get('partI', k)
    if _h is not None: rgb = _h[0].astype(np.float32) / 255; a = _h[1].astype(np.float32) / 255; F = _h[2]
    gx, gy = ANCH[k]['gx'], ANCH[k]['gy']
    # soft edges still carry the tile's navy: take it out, so no blue fringe shows on another colour
    nb = np.array(ANCH[k]['bg'], np.float32) / 255
    if not CLEAN and F == 1: rgb = np.where(a[:, :, None] > 0.02, np.clip((rgb - (1 - a[:, :, None]) * nb) / np.maximum(a[:, :, None], 0.02), 0, 1), rgb)
    # the ground shadow and black lines become plain darkness, so the shadow takes the new background's colour
    rgb = np.where((rgb.mean(axis=2, keepdims=True) < 0.1), 0.0, rgb)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = w0 - 1 - gx
    SC = SCALE / F   # the sharp redraw is F x bigger, so it is enlarged F x less
    h, w = a.shape; nh, nw = round(h * SC), round(w * SC)
    # bilinear resize
    ys = np.clip((np.arange(nh) + 0.5) / SC - 0.5, 0, h - 1); xs = np.clip((np.arange(nw) + 0.5) / SC - 0.5, 0, w - 1)
    y0 = ys.astype(int); x0 = xs.astype(int); y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    def rs(m):
        m = m if m.ndim == 3 else m[:, :, None]
        return (m[y0][:, x0] * (1 - fx) + m[y0][:, x1] * fx) * (1 - fy) + (m[y1][:, x0] * (1 - fx) + m[y1][:, x1] * fx) * fy
    if CLEAN:   # line poses up by the centre of the cream body, not the shadow (the shadows sit unevenly)
        body = (a > 0.9) & (rgb[:, :, 0] > 0.8) & (rgb[:, :, 1] > 0.65) & (rgb[:, :, 2] > 0.55)
        if body.sum() > 500 * F * F: gx = (float(np.nonzero(body)[1].mean()) + 0.5) / F - 0.5
    pa = rs(a)   # resize with the colours multiplied by alpha, so the see-through edge keeps its own colour (2026-11-03)
    return np.where(pa > 1e-4, np.clip(rs(rgb * a[:, :, None]) / np.maximum(pa, 1e-4), 0, 1), 0), pa, gx * SCALE, gy * SCALE
BG = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', D + '/empty_bg.png', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
if os.environ.get('BGCOLOR'):
    c = np.array([int(os.environ['BGCOLOR'][i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
    if os.environ.get('FLAT'): BG = np.broadcast_to(c, BG.shape).copy()          # one exact colour, no grain at all
    else:
        lum = BG.mean(axis=2, keepdims=True); BG = np.clip(c * (1 + 0.2 * (lum / lum.mean() - 1)), 0, 1)   # the colour, with only a faint grain
if os.environ.get('GLOW'):   # a soft light of this colour behind the character
    gc = np.array([int(os.environ['GLOW'][i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
    yy = (np.arange(H, dtype=np.float32) - 620)[:, None]; xx = (np.arange(W, dtype=np.float32) - 250)[None, :]
    g = (np.exp(-(xx * xx + yy * yy * 1.4) / (2 * 380.0 ** 2)) * 0.95)[:, :, None]
    BG = BG * (1 - g) + gc * (BG / max(BG.mean(), 1e-3) * BG.mean() / max(BG.mean(), 1e-3)) * 0 + gc * g
# optional PLAN: where the character's body centre sits over time, its own left limit, and a right
# limit that follows the notes (the nearest visible note in the coming AHEAD seconds, minus GAP)
PLAN = json.load(open(os.environ['PLAN'])) if os.environ.get('PLAN') else None
if PLAN:
    SCALE *= PLAN['grow']; LEFTLIM = PLAN['left']
    _nl = TM.note_left(os.path.join(os.path.dirname(os.environ['PLAN']), PLAN['notes']))
    def right_limit(ts, t1):   # the nearest note from the pose's start to its end, and AHEAD seconds beyond
        f0 = int(ts * FPS); f1 = min(len(_nl) - 1, int((t1 + PLAN['ahead']) * FPS) + 1)
        vals = [v for v in _nl[f0:f1 + 1] if v is not None]
        return min(W, (min(vals) if vals else W) - PLAN['gap'])
    def plan_centre(ts):
        for t0, t1, c0, c1 in PLAN['stretches']:
            if t0 <= ts + 1e-6 < t1: return c0 + (c1 - c0) * min(1, (ts - t0) / (t1 - t0))
        return PLAN['stretches'][-1][3]
CUTMASK = np.clip((np.arange(W, dtype=np.float32) - CUT) / FEATHER, 0, 1)[None, :, None]
_cache = {}
PLACED = {}   # slot -> (leftmost, rightmost, right limit), for checking
# ---- further right where the notes leave room (2026-11-11), on top of the plan's hand-set centres; made by ../stage.py
# as in part II. For every pose: how far it could move before its outline comes within the plan's gap of the nearest
# note. He stands up to RIGHT_I px further right where that room is there, and changes place only on poses that
# travel: the walks (the way he faces), the hops, the jumps and the big leap. Standing, squatting, juggling and
# sitting hold their spot. He ends at the plan's 560 px, where the chase picks him up. RIGHT_I=0 turns it off.
import stage
RIGHT_I, GAP_R = float(os.environ.get('RIGHT_I', 120)), int(os.environ.get('GAP_I', 130))   # standing further right, he lets the notes come as close as in part II
MOVES = {(A, 12): 'walk', (A, 13): 'walk', (A, 14): 'walk', (A, 15): 'walk', (A, 16): 'walk',            # the stroll out and back
         (A, 4): ('free', 60), (A, 6): ('free', 60), (A, 7): ('free', 60),                                # warm-up jumps
         (B, 1): ('free', 50), (B, 2): ('free', 50), (B, 3): ('free', 50), (B, 4): ('free', 150),         # hops, the big leap
         (C, 4): ('free', 60), (C, 6): ('free', 60), (C, 8): ('free', 60),                                # bounces
         (C, 11): 'walk', (C, 12): 'walk', (C, 13): 'walk', (C, 14): 'walk'}                              # the walk to where the chase finds him
def _move(e):
    m = MOVES.get((e[1], e[2]), ('hold',))
    return (('left' if e[4] else 'right'), 50, 18) if m == 'walk' else m
def _span(e):   # (pose start, end, the plan's centre)
    ts = max(0.0, e[0]); t1 = next((s[0] for s in SHEET if s[0] > e[0] + 1e-6), e[0] + 0.4)
    return ts, t1, round(plan_centre(ts))
def _room(e):
    ts, t1, x = _span(e); rgb, a, gx, gy = scaled(e[1], e[2], e[4])
    cols = np.nonzero(a[:, :, 0].max(0) > 0.05)[0]; ox = round(x - gx); ox += max(0, LEFTLIM - (ox + cols.min()))
    return float(right_limit(ts, t1) + PLAN['gap'] - GAP_R - (ox + cols.max()))
SHIFT_RIGHT = {}
if PLAN and RIGHT_I > 0:
    _last = max(i for i, e in enumerate(SHEET) if _move(e)[0] != 'hold') + 1          # after his last step he is where the plan ends
    _s = stage.plan([e[0] for e in SHEET], [_span(e)[2] for e in SHEET], [_room(e) for e in SHEET], [_move(e) for e in SHEET],
                    RIGHT_I, fixed={i: 0 for i in range(_last, len(SHEET))})
    SHIFT_RIGHT = {e[0]: int(v) for e, v in zip(SHEET, _s)}
def character_frame(t):
    e = pose_at(t); _, sh, po, x, fl = e
    rlim = RIGHTLIM
    if PLAN:   # one position per pose, worked out when it starts, so he never moves while a pose is held (2026-11-11)
        ts, t1, x = _span(e); x += SHIFT_RIGHT.get(e[0], 0); rlim = int(right_limit(ts, t1)) + (PLAN['gap'] - GAP_R if SHIFT_RIGHT.get(e[0], 0) else 0)
    key = (sh, po, x, fl, rlim)
    if key not in _cache:
        rgb, a, gx, gy = scaled(sh, po, fl)
        img = BG.copy(); oy, ox = round(GROUND - gy), round(x - gx)
        cols = np.nonzero(a[:, :, 0].max(0) > 0.05)[0]          # the whole outline, speed lines and sparkles included
        left, right = ox + cols.min(), ox + cols.max()
        if left < LEFTLIM: ox += LEFTLIM - left
        elif right > rlim: ox -= right - rlim
        PLACED[round(t * 5 + 1e-6)] = (ox + int(cols.min()), ox + int(cols.max()), rlim)
        h, w = a.shape[:2]; y0, x0 = max(0, oy), max(0, ox); y1, x1 = min(H, oy + h), min(W, ox + w)
        sa = a[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - sa) + rgb[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * sa
        _cache.clear(); _cache[key] = img
    return _cache[key]
def work(args):
    i, buf = args; t = TM.old(i / FPS)
    v = np.clip((np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
    if SHIFT: v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
    m = v.max(axis=2, keepdims=True); a = np.clip((m - 0.02) / 0.98, 0, 1) * CUTMASK
    col = np.where(m > 0, v / np.maximum(m, 1e-4), 0)
    out = character_frame(t) * (1 - a) + col * a
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
if __name__ == '__main__':
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-t', str(TM.new(DUR)), '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    if os.environ.get('LOSSLESS'):   # exact RGB, every pixel as computed (for editing; not every player opens it)
        venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    else:                            # standard H.264, colour standard stated so players don't guess
        venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-t', str(TM.new(DUR)), '-i', src, '-map', '0:v', '-map', '1:a?', *venc, '-c:a', 'aac', '-b:a', '192k', '-shortest', dst], stdin=subprocess.PIPE)
    def frames():
        i = 0
        while True:
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b; i += 1
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=6): enc.stdin.write(out)   # chunks of 6 frames = one pose
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst)
