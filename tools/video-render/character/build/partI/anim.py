# Part I of the étude: the cut-out character animated at 5 poses a second on
# the empty navy background, timed to the music, with the notes on top
# (moved so they are hit at 50% of the width and gone at 25%).
# Usage: anim.py video out.mp4 [seconds]
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
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
SHEET = [
    (0.0, A, 1), (0.6, A, 2), (0.8, A, 1), (1.2, A, 2), (1.4, A, 3),
    (1.8, A, 4), (2.2, A, 5), (2.8, A, 6), (3.2, A, 5), (3.4, A, 7), (3.6, A, 8), (3.8, A, 9),
    (4.2, A, 10), (4.4, A, 11),
    (5.4, A, 12, 252), (5.6, A, 13, 260), (6.0, A, 12, 268), (6.2, A, 13, 275), (6.4, A, 12, 282), (6.6, A, 13, 282),
    (6.8, A, 14, 276, 1), (7.0, A, 15, 270, 1), (7.2, A, 16, 264, 1), (7.4, A, 15, 258, 1), (7.6, A, 14, 252, 1),
    (7.8, A, 15, 249, 1), (8.0, A, 16, 244, 1), (8.2, A, 15, 240, 1), (8.4, A, 1),
    (8.6, B, 1), (8.8, B, 2), (9.0, B, 3), (9.2, B, 2), (9.4, B, 1), (9.6, B, 4), (10.2, B, 5),
    (10.4, B, 6), (10.6, B, 7), (10.8, B, 6), (11.0, B, 7), (11.2, B, 8), (11.6, B, 9), (11.8, B, 8),
    (12.2, B, 10), (12.4, B, 11), (12.8, B, 12), (13.0, B, 13), (13.2, B, 12), (13.6, B, 11),
    (14.0, B, 16), (14.2, B, 14), (14.6, B, 12), (14.8, B, 13), (15.0, B, 15), (16.0, B, 16), (16.2, B, 15),
    (16.8, C, 1), (17.0, C, 2), (17.4, C, 3), (17.6, C, 2), (17.8, C, 3), (18.0, C, 2), (18.2, C, 3),
    (18.4, C, 4), (18.8, C, 5), (19.4, C, 6), (19.8, C, 7), (20.8, C, 8), (21.2, C, 9), (21.6, C, 10),
] + [(22.8 + 0.2 * k, C, 11 + k % 4, 243 + 3 * k) for k in range(13)] + [
    (25.4, C, 15, 280), (25.6, C, 16, 280), (25.8, C, 15, 280), (26.0, C, 16, 280)]
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
def scaled(sheet, pose, flip):
    k = f'{sheet}_{pose}'
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    gx, gy = ANCH[k]['gx'], ANCH[k]['gy']
    # soft edges still carry the tile's navy: take it out, so no blue fringe shows on another colour
    nb = np.array(ANCH[k]['bg'], np.float32) / 255
    if not CLEAN: rgb = np.where(a[:, :, None] > 0.02, np.clip((rgb - (1 - a[:, :, None]) * nb) / np.maximum(a[:, :, None], 0.02), 0, 1), rgb)
    # the ground shadow and black lines become plain darkness, so the shadow takes the new background's colour
    rgb = np.where((rgb.mean(axis=2, keepdims=True) < 0.1), 0.0, rgb)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
    h, w = a.shape; nh, nw = round(h * SCALE), round(w * SCALE)
    # bilinear resize
    ys = np.clip((np.arange(nh) + 0.5) / SCALE - 0.5, 0, h - 1); xs = np.clip((np.arange(nw) + 0.5) / SCALE - 0.5, 0, w - 1)
    y0 = ys.astype(int); x0 = xs.astype(int); y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    def rs(m):
        m = m if m.ndim == 3 else m[:, :, None]
        return (m[y0][:, x0] * (1 - fx) + m[y0][:, x1] * fx) * (1 - fy) + (m[y1][:, x0] * (1 - fx) + m[y1][:, x1] * fx) * fy
    if CLEAN:   # line poses up by the centre of the cream body, not the shadow (the shadows sit unevenly)
        body = (a > 0.9) & (rgb[:, :, 0] > 0.8) & (rgb[:, :, 1] > 0.65) & (rgb[:, :, 2] > 0.55)
        if body.sum() > 500: gx = float(np.nonzero(body)[1].mean())
    return rs(rgb), rs(a), gx * SCALE, gy * SCALE
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
    _nl = json.load(open(os.path.join(os.path.dirname(os.environ['PLAN']), PLAN['notes'])))['noteLeft']
    def right_limit(ts):
        f0 = int(ts * FPS); f1 = min(len(_nl) - 1, int((ts + 0.2 + PLAN['ahead']) * FPS) + 1)
        vals = [v for v in _nl[f0:f1 + 1] if v is not None]
        return min(W, (min(vals) if vals else W) - PLAN['gap'])
    def plan_centre(ts):
        for t0, t1, c0, c1 in PLAN['stretches']:
            if t0 <= ts + 1e-6 < t1: return c0 + (c1 - c0) * min(1, (ts - t0) / (t1 - t0))
        return PLAN['stretches'][-1][3]
CUTMASK = np.clip((np.arange(W, dtype=np.float32) - CUT) / FEATHER, 0, 1)[None, :, None]
_cache = {}
PLACED = {}   # slot -> (leftmost, rightmost, right limit), for checking
def character_frame(t):
    _, sh, po, x, fl = pose_at(t)
    rlim = RIGHTLIM
    if PLAN:
        ts = int(t * 5 + 1e-6) / 5                     # the pose slot this frame is in
        x = round(plan_centre(ts)); rlim = int(right_limit(ts))
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
    i, buf = args; t = i / FPS
    v = np.clip((np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
    if SHIFT: v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
    m = v.max(axis=2, keepdims=True); a = np.clip((m - 0.02) / 0.98, 0, 1) * CUTMASK
    col = np.where(m > 0, v / np.maximum(m, 1e-4), 0)
    out = character_frame(t) * (1 - a) + col * a
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
if __name__ == '__main__':
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-t', str(DUR), '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    if os.environ.get('LOSSLESS'):   # exact RGB, every pixel as computed (for editing; not every player opens it)
        venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    else:                            # standard H.264, colour standard stated so players don't guess
        venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-t', str(DUR), '-i', src, '-map', '0:v', '-map', '1:a', *venc, '-c:a', 'aac', '-b:a', '192k', '-shortest', dst], stdin=subprocess.PIPE)
    def frames():
        i = 0
        while True:
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b; i += 1
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=6): enc.stdin.write(out)   # chunks of 6 frames = one pose
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst)
