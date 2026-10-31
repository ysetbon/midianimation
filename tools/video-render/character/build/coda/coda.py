# The Coda (102.55 s to the end): the Black Key Piano floats down like a leaf, happy and
# friendly now; the White Key Piano welcomes him; on the final four single notes the Brown
# Piano tiptoes in from the left, and on the last chords all three hug until the end.
# The stage widens as the music thins out: notes now vanish at about half the width, so
# three characters fit side by side without shrinking anyone.
# Usage: coda.py source.mp4 out.mkv [start_s end_s]     coda.py --still t out.png
import os, sys, json, subprocess, numpy as np, multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
import timemap as TM   # choreography time <-> video time (TIMEMAP)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D + '/../chase')
from chase import resize, paste, shadow, YY, XX
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, FEATHER, LEFT, GROUND = 384, 24, 35, 960
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
BG0 = hexc('1f4a5c')                                                   # part III's petrol
BG = hexc(os.environ.get('BG', '4a4470'))                              # the Coda's calm colour: lavender dusk (chosen)
BGT = os.environ.get('BGT', '1')                                       # how it arrives: 1, a glide with the crop (chosen)
Z = dict(np.load(D + '/coda_sprites.npz').items()); ANCH = json.load(open(D + '/coda_anchors.json'))
SCALE = {'J': 1.663,    # the White Key Piano: his card as tall as in part III
         'B': 1.83,     # the Black Key Piano (each pose then corrected to 100%, see BFIX)
         'Q': 2.577 * 379 / 354,   # the Brown Piano at 100%: as tall as in the sharp hug frames (front 379 px)
         'X': 3.0}      # all three hugging, sized so the Black Key Piano is at 100% in it (cap 260 px)
HX = 617                # the White Key Piano's centre in the hug (the group then spans 35-1007 px)
SCALE['Y'] = SCALE['V'] = 260 / 171 * 0.893   # the sharp hug frames (two 2x2 sheets): both keys as tall as in the frame before the hug
HUG_GX_Y = 380          # the White Key Piano's centre inside the sharp hug drawings
SHARP = {2: 'Y_1', 3: 'Y_2', 4: 'Y_3', 10: 'Y_4', 5: 'V_1', 9: 'V_2', 12: 'V_3', 16: 'V_4'}   # the old hug frames, replaced by the sharp ones
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
from crop import cut_at   # how the vanish line widens: CROP=A..E (see crop.py); the chosen one is B
# ---- the exposure sheets: (time, pose, body centre x, height above the ground, mirrored, may leave the frame)
def P(t, k, x, y=0, fl=0, ex=0): return (t, k, x, y, fl, ex)
# he steps over to the left to make room for the fall, then walks right again as the Brown Piano arrives
WHITE = [P(102.50, 'J_2', 214), P(103.01, 'J_2', 214),   # pointing up from the Coda's first note (102.55 s)
         P(104.47, 'J_3', 215), P(105.28, 'J_4', 215), P(105.98, 'J_3', 215),
         P(106.45, 'J_5', 215), P(107.08, 'J_6', 215), P(108.34, 'J_7', 260), P(108.90, 'J_8', 330), P(109.41, 'J_9', 420),
         P(110.42, 'J_11', 500),
         P(110.90, 'J_12', 545), P(111.35, 'J_13', 555), P(111.60, 'J_15', 560), P(112.78, None, 0)]
# floating down like a leaf from the glittering high note (103.52 s), a swing on every note of the falling cascade
# he appears 2 frames after the notes have fully made room (crop option B: done at 103.30 s)
import crop as _crop
_full = next(f for f in range(3070, 3200) if _crop.cut_at(f / 30) >= _crop.TO)
FALL = [(_full + 2) / 30, 103.73, 103.90, 104.04, 104.17, 104.33, 104.47, 104.62, 104.79, 104.96, 105.10, 105.28, 105.44, 105.62,
        105.80, 105.98, 106.19, 106.45, 106.70]
BLACK = [P(102.50, None, 0)] + [P(t, f'B_{1 + i % 8}', 620 + (35 if i % 2 else -35), 640 * (1 - (t - FALL[0]) / (107.08 - FALL[0])) ** 0.9, ex=1)
                               for i, t in enumerate(FALL)] + [
         P(107.08, 'B_9', 620), P(107.60, 'B_10', 620), P(108.34, 'B_11', 640), P(108.90, 'B_12', 680), P(109.41, 'B_13', 720),
         P(110.42, 'B_12', 750), P(111.35, 'B_10', 765), P(111.60, 'B_14', 765), P(112.78, None, 0)]
# tiptoeing in from the left edge, a step on each of the final four single notes
PIANO = [P(102.50, None, 0), P(109.41, 'Q_1', -170, ex=1), P(110.42, 'Q_2', 20, ex=1), P(110.90, 'Q_3', 160, ex=1), P(111.35, 'Q_4', 250),
         P(111.60, 'Q_6', 300), P(112.78, None, 0)]
# all three hugging, from the last chords to the end; the White Key Piano stays where he stood (x 560)
HUG = [P(102.50, None, 0), P(112.78, 'X_3', 560), P(113.20, 'X_4', 560), P(113.80, 'X_5', 560),
       P(114.40, 'X_6', 560), P(114.90, 'X_7', 560), P(115.40, 'X_6', 560), P(115.90, 'X_7', 560), P(116.40, 'X_9', 560),
       P(117.00, 'X_10', 560)] + [
       # once the last note has gone (117.5 s), just two frames, rocking gently to the end
       P(117.50 + 0.6 * i, ('X_15', 'X_16')[i % 2], 560) for i in range(8)]
HUG_IN = (112.78, 112.78)                     # straight into the hug on the final chord, like a new frame
HUG_GX = 203                                  # the White Key Piano's centre inside the hug drawing
# the end: once the last note has gone, the stars frame, held to the end
END = [P(117.50, 'V_4', 617)]
# ENDING picks how the final four notes are used (see the Coda Ending page)
ENDING = os.environ.get('ENDING', 'B')   # chosen: B
if ENDING == 'A':     # the Brown Piano steps in on the final four notes; all three together from the last chord
    HUG = [h for h in HUG if h[0] < 117.5] + END
elif ENDING == 'B':   # the Brown Piano tiptoes in while the 108.34 s chord rings; the final four notes are four frames of all three
    WHITE = [w for w in WHITE if w[0] < 107.5] + [P(107.60, 'J_7', 320), P(108.00, 'J_8', 430), P(108.34, 'J_9', 520),
             P(108.70, 'J_11', 590), P(109.00, 'J_13', HX), P(109.41, None, 0)]
    BLACK = [b for b in BLACK if b[0] < 107.5] + [P(107.60, 'B_10', 680), P(108.00, 'B_11', 750), P(108.34, 'B_12', 800),
             P(108.70, 'B_13', 842), P(109.41, None, 0)]
    PIANO = [P(102.50, None, 0), P(108.34, 'Q_1', -200, ex=1), P(108.54, 'Q_2', -60, ex=1), P(108.74, 'Q_3', 80, ex=1),
             P(108.94, 'Q_4', 220), P(109.14, 'Q_6', 311), P(109.41, None, 0)]
    # which group frames land on 109.41, 110.42, 110.90, 111.35 (the final four notes), 111.60 (bass chord),
    # 112.78 (last chord) and 114.80 (while it rings); BSEQ picks another order (see the Coda Frames page)
    SEQ = [int(n) for n in os.environ.get('BSEQ', '2,3,4,10,5,9,12').split(',')]   # chosen: B6, hearts to the end
    HUG = [P(102.50, None, 0)] + [P(t, SHARP.get(n, f'X_{n}'), HX) for t, n in zip((109.41, 110.42, 110.90, 111.35, 111.60, 112.78, 114.80), SEQ)] + END
    HUG_IN = (109.41, 109.41)
elif ENDING == 'C':   # the Brown Piano takes two big steps (109.41, 110.42); the last four sounds are four frames of all three
    WHITE = [w for w in WHITE if w[0] < 109.0] + [P(109.41, 'J_9', 440), P(110.42, 'J_13', 560), P(110.90, None, 0)]
    BLACK = [b for b in BLACK if b[0] < 109.0] + [P(109.41, 'B_13', 740), P(110.42, 'B_10', 765), P(110.90, None, 0)]
    PIANO = [P(102.50, None, 0), P(109.41, 'Q_2', 0, ex=1), P(110.42, 'Q_6', 300), P(110.90, None, 0)]
    HUG = [P(102.50, None, 0), P(110.90, 'X_1', 560), P(111.35, 'X_2', 560), P(111.60, 'X_3', 560), P(112.78, 'X_4', 560),
           P(114.80, 'X_10', 560)] + END
    HUG_IN = (110.90, 110.90)
def at(sheet, t):
    cur = None
    for e in sheet:
        if e[0] <= t + 1e-6: cur = e
        else: break
    return cur
# the Black Key Piano at 100% in every pose (falling poses are tilted, so they take his standing poses' correction)
sys.path.insert(0, D + '/../chase')
import sizefix
BFIX, _ = sizefix.black_key_fix(Z, [f'B_{i}' for i in range(1, 17)], SCALE['B'], turned=tuple(f'B_{i}' for i in range(1, 9)))
_sprite = {}
def sprite(k, flip):
    key = (k, flip)
    if key in _sprite: return _sprite[key]
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    an = ANCH[k]; gx, gy = (HUG_GX if k[0] == 'X' else HUG_GX_Y if k[0] in 'YV' else an['gx']), an['gy']; s = SCALE[k[0]] * BFIX.get(k, 1.0)
    if k[0] in 'JB': rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = a.shape[1] - 1 - gx
    r = (resize(rgb, s), resize(a, s)[:, :, 0], gx * s, gy * s)
    if len(_sprite) > 40: _sprite.clear()
    _sprite[key] = r
    return r
PLACED = []
def draw(img, sheet, t, name, shade=0.28):
    e = at(sheet, t)
    if not e or not e[1]: return
    _, k, x, yoff, fl, ex = e
    rgb, a, gx, gy = sprite(k, fl)
    ox, oy = round(x - gx), round(GROUND - gy - yoff)
    cols = np.nonzero(a.max(0) > 0.05)[0]
    if not ex and ox + cols.min() < LEFT: ox += LEFT - (ox + cols.min())
    PLACED.append((round(t, 3), name, k, ox + int(cols.min()), ox + int(cols.max())))
    shadow(img, ox + (cols.min() + cols.max()) / 2, (cols.max() - cols.min()) * 0.85, shade * max(0.25, 1 - yoff / 400))
    paste(img, rgb, a, ox, oy)
import crop as _c
def _crop_progress(t):   # 0..1, exactly as the notes' vanish line moves (crop option B: 102.55-103.30 s)
    return (_c.cut_at(t) - _c.FROM) / (_c.TO - _c.FROM)
def background(t):
    if BGT == '1':   u = _crop_progress(t)                                   # one glide with the crop, whole screen
    elif BGT == '2':                                                          # a soft wipe from left to right, in step with the crop
        p = _crop_progress(t); edge = -300 + (W + 600) * p
        m = np.clip((edge - np.arange(W, dtype=np.float32)) / 300 + 0.5, 0, 1)[None, :, None]
        return np.broadcast_to(BG0 * (1 - m) + BG * m, (H, W, 3)).astype(np.float32)
    elif BGT == '3':                                                          # a glow spreading from where he will land, in step with the crop
        p = _crop_progress(t); r = 2600 * p ** 1.3
        d = np.sqrt((XX - 620) ** 2 + ((YY - 900) * 1.15) ** 2)
        m = np.clip((r - d) / 420 + 0.5, 0, 1)[:, :, None] if p < 1 else np.ones((H, W, 1), np.float32)
        return (BG0 * (1 - m) + BG * m).astype(np.float32)
    elif BGT == '4':                                                          # slowly, while he floats down (103.37 s to his landing at 107.08 s)
        u = min(1, max(0, (t - FALL[0]) / (107.08 - FALL[0]))); u = u * u * (3 - 2 * u)
    elif BGT == '5':                                                          # in four steps with the crop
        p = _crop_progress(t); u = np.floor(p * 4 + 1e-6) / 4
    else:                                                                     # a cut, the moment the crop is full
        u = 1.0 if _crop_progress(t) >= 1 else 0.0
    return np.broadcast_to(BG0 * (1 - u) + BG * u, (H, W, 3)).astype(np.float32)
def frame(t, notes_rgb=None):
    img = np.array(background(t), np.float32)
    if t < HUG_IN[1]:
        draw(img, PIANO, t, 'piano'); draw(img, WHITE, t, 'white'); draw(img, BLACK, t, 'black')
    if t >= HUG_IN[0]:
        hug = np.array(background(t), np.float32); draw(hug, HUG, t, 'hug', 0.32)
        img = hug
    if notes_rgb is not None:
        v = np.clip((notes_rgb.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)
        v = np.concatenate([np.zeros((H, SHIFT, 3), np.float32), v[:, :W - SHIFT]], axis=1)
        m = v.max(2, keepdims=True); na = np.clip((m - 0.02) / 0.98, 0, 1) * np.clip((np.arange(W, dtype=np.float32) - cut_at(t)) / FEATHER, 0, 1)[None, :, None]
        img = img * (1 - na) + np.where(m > 0, v / np.maximum(m, 1e-4), 0) * na
    if t >= FADE[0]:   # the end: black spreads out in a soft circle from where the Black Key Piano landed, over everything
        p = min(1.0, (t - FADE[0]) / (FADE[1] - FADE[0]))
        r = 2600 * p ** 1.3; d = np.sqrt((XX - 620) ** 2 + ((YY - 900) * 1.15) ** 2)
        m = np.clip((r - d) / 420 + 0.5, 0, 1)[:, :, None] if p < 1 else 1.0
        img = img * (1 - m)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
FADE = (119.8, 121.8)   # fully black from 121.8 s to the end (122.13 s)
def grab(src, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t - 0.5 / FPS:.4f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
SRC = os.environ.get('SRC', D + '/../etude1_final_v3.mp4')
def work(args):
    i, buf, f0 = args
    return frame(TM.old((f0 + i) / FPS), np.frombuffer(buf, np.uint8).reshape(H, W, 3)).tobytes()
if __name__ == '__main__':
    if sys.argv[1] == '--still':
        from PIL import Image
        t = float(sys.argv[2]); Image.fromarray(frame(t, grab(SRC, TM.new(t)))).save(sys.argv[3]); sys.exit()
    src, dst = sys.argv[1:3]
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (3077 / FPS, 3664 / FPS)
    f0, f1 = round(TM.new(t0) * FPS), round(TM.new(t1) * FPS); n = f1 - f0
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24', dst], stdin=subprocess.PIPE)
    def frames():
        for i in range(n):
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b, f0
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=4): enc.stdin.write(out)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst, n, 'frames')
