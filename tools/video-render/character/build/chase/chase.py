# The I -> II crossing of the étude: the black character sneaks up on the white
# one and chases him away, poses changing on the notes, over a background that
# turns from part I's raspberry rose to part II's colour as the black one's
# "aura" spreads from him and fills the screen.
# Placement is automatic, as in part I: every pose's whole outline is kept right
# of LEFT and left of a limit that follows the notes (the nearest note in the
# coming AHEAD seconds, minus GAP). Only the entrance and the exit cross the left edge.
# Usage: chase.py source.mp4 out.mp4 [start_s end_s]     env: BG2=hex, LOSSLESS=1
#        chase.py --still t out.png                      (one frame, for previews)
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, CUT, FEATHER = 384, 480, 24            # notes hit at 60% of the width, gone at 25%
LEFT, GAP, AHEAD, GROUND = 35, 190, 1.1, 960
S1, S2 = 2.036, float(os.environ.get('S2', 1.35))                        # part I's size; the wider shot once there are two of them
ZOOM = (26.35, 27.25)                        # the camera pulls back as the black one creeps in
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
BG1 = hexc(os.environ.get('BG1', '8c3b55')); BG2 = hexc(os.environ.get('BG2', '8a4336'))
Z = dict(np.load(D + '/chase_sprites.npz').items()); ANCH = json.load(open(D + '/chase_anchors.json'))
# each sheet drawn at its own size: the white one's cream body as tall as in part I (170 px in part I's
# sheets, at S1); the black one keeps his scale relative to that, a head taller as in his reference
_wh = float(np.median([v['bodyH'] for k, v in ANCH.items() if k.startswith('W_')]))
MULT = {'W': 170.0 / _wh, 'K': 1.0}
NL = json.load(open(D + '/notes.json'))['noteLeft']
# ---- the exposure sheets: (time, pose, body centre x, height above the ground, mirrored, may leave the frame)
def P(t, p, x, y=0, fl=0, ex=0): return (t, p, x, y, fl, ex)
WHITE = [
    P(26.0, 1, 560), P(26.61, 2, 560), P(27.0, 1, 560), P(27.38, 2, 560),       # oblivious: waving, strolling
    P(27.52, 3, 560, fl=1),                                                       # chord: startled, turns toward the noise
    P(27.89, 4, 560, fl=1), P(28.16, 3, 565, fl=1), P(28.29, 4, 565, fl=1),        # scared
    P(28.55, 4, 575, 230, fl=1), P(28.68, 4, 580, fl=1),                            # the big chord: jumps with fright
] + [P(t, 5 + k % 4, 585 + 4 * k) for k, t in enumerate(                            # runs for it (toward the notes)
    [28.82, 28.92, 29.08, 29.2, 29.34, 29.46, 29.6, 29.73, 29.87, 29.99, 30.14, 30.25, 30.39])] + [
    P(30.51, 9, 650), P(30.65, 9, 650),                                            # skids: the notes block the way
    P(30.91, 10, 470, 270, fl=1), P(31.02, 10, 300, 210, fl=1),                    # strongest chord: leaps over the black one
    P(31.16, 11, 130, fl=1), P(31.29, 12, 130), P(31.54, 12, 135, fl=1),           # lands, relieved, panting
    P(31.83, 13, 135), P(32.08, 14, 130, fl=1),                                    # a worried look back, ready to dash
    P(32.22, 15, 40, fl=1, ex=1), P(32.34, 16, -180, fl=1, ex=1), P(32.47, 16, -600, fl=1, ex=1), P(32.6, None, 0)]
BLACK = [P(26.0, None, 0),
    # peeks in from the left edge and creeps closer, a step per high note
    P(26.35, 1, -170, ex=1), P(26.48, 2, -125, ex=1), P(26.61, 1, -85, ex=1), P(26.74, 2, -50, ex=1),
    P(26.87, 1, -20, ex=1), P(27.0, 2, 10, ex=1), P(27.12, 3, 30, ex=1), P(27.26, 4, 50, ex=1), P(27.38, 2, 70, ex=1),
    P(27.52, 4, 150), P(27.89, 1, 160), P(28.29, 3, 170),                          # caught on the chord: freezes, shushes
    P(28.55, 5, 260),                                                              # the big chord: a stomp
] + [P(t, (6, 7, 8, 9)[k % 4] if t != 29.6 else 9, 265 + 9 * k) for k, t in enumerate(   # the chase
    [28.82, 28.92, 29.08, 29.2, 29.34, 29.46, 29.6, 29.73, 29.87, 29.99, 30.14, 30.25, 30.39, 30.51, 30.65])] + [
    P(30.78, 10, 430),                                                             # lunges for him
    P(30.91, 11, 470), P(31.42, 12, 460),                                          # grabs at nothing; hands on hips
    P(31.69, 13, 450, fl=1), P(32.08, 14, 440),                                    # glares after him; the anger mark
    P(32.59, 15, 380), P(33.11, 16, 340),                                          # arms cross; "hmph" as part II begins
    P(33.5, 15, 330), P(34.0, 16, 330), P(34.4, 15, 330), P(34.8, 16, 330)]
def at(sheet, t):
    cur, nxt = sheet[0], None
    for i, e in enumerate(sheet):
        if e[0] <= t + 1e-6: cur, nxt = e, (sheet[i + 1][0] if i + 1 < len(sheet) else t + 0.4)
        else: break
    return cur, nxt
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
# once the white one has run off, the camera moves back in until the black one stands as tall as the
# white one did in part I (about 475 px from cap to shoes), reached on the arrival chord at 33.11
S3, ZOOM_IN = 475 / 256, (32.47, 33.11)
NOSHRINK = bool(os.environ.get('NOSHRINK'))   # no camera moves: both at full size the whole time
if NOSHRINK: MULT['K'] = S3 / S1                # the black one as tall as the white one, from his first step
def cam_scale(t):
    if NOSHRINK: return S1
    return S1 + (S2 - S1) * ease((t - ZOOM[0]) / (ZOOM[1] - ZOOM[0])) + (S3 - S2) * ease((t - ZOOM_IN[0]) / (ZOOM_IN[1] - ZOOM_IN[0]))
def right_limit(t0, t1):   # nearest note while this pose shows, and AHEAD seconds beyond
    vals = [v for v in NL[int(t0 * FPS):min(len(NL), int((t1 + AHEAD) * FPS) + 2)] if v is not None]
    return min(W, (min(vals) if vals else W) - GAP)
def resize(m, s):
    h, w = m.shape[:2]; nh, nw = max(1, round(h * s)), max(1, round(w * s))
    ys = np.clip((np.arange(nh) + 0.5) / s - 0.5, 0, h - 1); xs = np.clip((np.arange(nw) + 0.5) / s - 0.5, 0, w - 1)
    y0 = ys.astype(int); x0 = xs.astype(int); y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    m = m if m.ndim == 3 else m[:, :, None]
    return (m[y0][:, x0] * (1 - fx) + m[y0][:, x1] * fx) * (1 - fy) + (m[y1][:, x0] * (1 - fx) + m[y1][:, x1] * fx) * fy
_sprite = {}
def sprite(name, pose, flip, s, air):
    key = (name, pose, flip, round(s, 4), air)
    if key in _sprite: return _sprite[key]
    k = f'{name}_{pose}'
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    an = ANCH[k]; gx, gy = an['gx'], an['gy']
    rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)              # lines and shadow: plain darkness
    if air:   # in the air the drawn shadow can't come along (it lies on the ground line, below the feet)
        low = np.arange(a.shape[0])[:, None] >= gy - 3
        a = np.where(low & (rgb.sum(2) == 0) & (a < 0.9), 0, a)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
    s = s * MULT[name]
    r = (resize(rgb, s), resize(a, s)[:, :, 0], gx * s, gy * s, an['bodyW'] * s)
    if len(_sprite) > 64: _sprite.clear()
    _sprite[key] = r
    return r
PLACED = []
def place(name, sheet, t, s):
    e, t1 = at(sheet, t)
    _, pose, x, yoff, fl, ex = e
    if pose is None: return None
    rgb, a, gx, gy, bw = sprite(name, pose, fl, s, yoff > 0)
    ox = round(x - gx); oy = round(GROUND - gy - yoff * s / S1)
    cols = np.nonzero(a.max(0) > 0.05)[0]; left, right = ox + cols.min(), ox + cols.max()
    rlim = right_limit(e[0], t1)
    if not ex:
        if right > rlim: ox -= right - rlim
        if ox + cols.min() < LEFT: ox += LEFT - (ox + cols.min())
    PLACED.append((round(t, 3), name, pose, ox + int(cols.min()), ox + int(cols.max()), rlim, ex))
    return rgb, a, ox, oy, yoff, bw
def paste(img, rgb, a, ox, oy):
    h, w = a.shape; y0, x0 = max(0, oy), max(0, ox); y1, x1 = min(H, oy + h), min(W, ox + w)
    if y1 <= y0 or x1 <= x0: return
    sa = a[y0 - oy:y1 - oy, x0 - ox:x1 - ox, None]
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - sa) + rgb[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * sa
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
def shadow(img, cx, width, strength):   # a soft ground shadow (the black one's sheet has none)
    g = np.exp(-(((XX - cx) / (width * 0.5)) ** 2 + ((YY - GROUND + 4) / 13) ** 2) * 2)
    img *= 1 - strength * g[:, :, None]
# ---- the background: part II's colour spreads out from the black one
AURA = {}
def aura_radius(t):
    # grows with him while he creeps and chases, bursts on the stomp, then fills the frame
    # as the white one runs off, complete on the arrival chord at 33.11
    r = 0 if t < 26.35 else 260 + 260 * ease((t - 26.35) / 2.2)
    if t >= 28.55: r += 120 * np.exp(-(t - 28.55) / 0.25) + 60
    if t >= 30.91: r += 120 * ease((t - 30.91) / 0.6)
    if t >= 31.83: r += 2400 * ease((t - 31.83) / (33.11 - 31.83)) ** 1.6
    return r
def background(t, bx):
    r = aura_radius(t)
    if r <= 0: return np.broadcast_to(BG1, (H, W, 3)).copy()
    d = np.sqrt((XX - bx) ** 2 + ((YY - 720) * 1.15) ** 2)
    m = np.clip((r - d) / 420 + 0.5, 0, 1); m = (m * m * (3 - 2 * m))[:, :, None]
    if t >= 33.11: return np.broadcast_to(BG2, (H, W, 3)).copy()
    # a little noise only inside the soft edge, so the gradient doesn't band; flat areas stay exact
    m = np.clip(m + (np.random.default_rng(int(t * FPS)).random((H, W, 1), np.float32) - 0.5) * (8 * m * (1 - m)) * 0.02, 0, 1)
    return BG1 * (1 - m) + BG2 * m
_last_bx = [0.0]
def frame(t, notes_rgb=None):
    s = cam_scale(t)
    k = place('K', BLACK, t, s); w = place('W', WHITE, t, s)
    if k: _last_bx[0] = k[2] + k[1].shape[1] / 2
    img = background(t, _last_bx[0] if k else -400)
    def draw_k():
        rgb, a, ox, oy, yoff, bw = k; shadow(img, ox + a.shape[1] / 2, bw * 1.1, 0.30); paste(img, rgb, a, ox, oy)
    def draw_w():
        rgb, a, ox, oy, yoff, bw = w
        shadow(img, ox + a.shape[1] / 2, bw * 0.9, 0.26 * max(0.3, 1 - yoff / 300))   # his sheet draws none either
        paste(img, rgb, a, ox, oy)
    order = [draw_w, draw_k] if 30.78 <= t < 30.91 else [draw_k, draw_w]   # his lunge reaches in front of the white one
    for d, c in zip(order, ([w, k] if order[0] is draw_w else [k, w])):
        if c: d()
    if notes_rgb is not None:
        v = np.clip((notes_rgb.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
        v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
        m = v.max(2, keepdims=True); na = np.clip((m - 0.02) / 0.98, 0, 1) * np.clip((np.arange(W, dtype=np.float32) - CUT) / FEATHER, 0, 1)[None, :, None]
        img = img * (1 - na) + np.where(m > 0, v / np.maximum(m, 1e-4), 0) * na
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
def grab(src, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t - 0.5 / FPS:.4f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
SRC = os.environ.get('SRC', D + '/../etude1_final_v3.mp4')
def work(args):
    i, buf, f0 = args
    t = (f0 + i) / FPS
    # the sheets are looked up by time, so each worker places the characters itself
    return frame(t, np.frombuffer(buf, np.uint8).reshape(H, W, 3)).tobytes()
if __name__ == '__main__':
    if sys.argv[1] == '--still':
        t = float(sys.argv[2]); from PIL import Image
        Image.fromarray(frame(t, grab(SRC, t))).save(sys.argv[3]); sys.exit()
    src, dst = sys.argv[1:3]
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (26.2333, 33.1333)
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    n = f1 - f0
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    if os.environ.get('LOSSLESS'): venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    else: venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{f0 / FPS:.4f}', '-t', f'{n / FPS:.4f}', '-i', src, '-map', '0:v', '-map', '1:a', *venc, '-c:a', 'aac', '-b:a', '192k', '-shortest', dst], stdin=subprocess.PIPE)
    def frames():
        for i in range(n):
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b, f0
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=4): enc.stdin.write(out)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst, n, 'frames')
