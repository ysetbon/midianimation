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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hd')); import hd as HD   # the sharp redraws (hd/make_hd.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
import timemap as TM   # choreography time <-> video time (TIMEMAP)
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
NL = TM.note_left(D + '/notes.json')
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
def resize_rgba(rgb, a, s):
    # resize with the colours multiplied by alpha, then divide it back out, so the see-through edge keeps its own
    # colour instead of mixing in the black of the empty pixels around the drawing (2026-11-03)
    pa = resize(a, s); prgb = resize(rgb * (a if a.ndim == 3 else a[:, :, None]), s)
    return np.where(pa > 1e-4, np.clip(prgb / np.maximum(pa, 1e-4), 0, 1), 0), pa[:, :, 0]
_sprite = {}
def sprite(name, pose, flip, s, air):
    key = (name, pose, flip, round(s, 4), air)
    if key in _sprite: return _sprite[key]
    k = f'{name}_{pose}'
    rgb = Z[k + '_rgb'].astype(np.float32) / 255; a = Z[k + '_a'].astype(np.float32) / 255
    w0 = a.shape[1]; F = 1   # the sharp redraw, if there is one: F x the old size, same anchors
    _h = HD.get('chase', k)
    if _h is not None: rgb = _h[0].astype(np.float32) / 255; a = _h[1].astype(np.float32) / 255; F = _h[2]
    an = ANCH[k]; gx, gy = an['gx'], an['gy']
    rgb = np.where(rgb.mean(2, keepdims=True) < 0.1, 0.0, rgb)              # lines and shadow: plain darkness
    if air:   # in the air the drawn shadow can't come along (it lies on the ground line, below the feet)
        low = np.arange(a.shape[0])[:, None] >= (gy - 3) * F
        a = np.where(low & (rgb.sum(2) == 0) & (a < 0.9), 0, a)
    if flip: rgb = rgb[:, ::-1]; a = a[:, ::-1]; gx = w0 - 1 - gx
    s = s * MULT[name]
    r = (*resize_rgba(rgb, a, s / F), gx * s, gy * s, an['bodyW'] * s)
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
# AURA_PLAN picks how the colour spreads (2026-11-13, options for the user; all times are choreography time, and the
# notes they follow are the ethude_1_27 notes of the crossing). A, the default, is the look chosen on 2026-10-25.
AURA_PLAN = os.environ.get('AURA', 'Y1')   # Y1, the user's own curve (2026-11-13); A is the look of 2026-10-25
_ARP = [30.96, 31.08, 31.19, 31.31, 31.42, 31.54, 31.66, 31.76]          # the rising arpeggio, E4 up to D7
_RUN = [29.22, 29.33, 29.45, 29.57, 29.68, 29.81, 29.92, 30.04, 30.14, 30.27, 30.38, 30.50, 30.59]   # the rising run
_LOUD = [(27.04, 102), (28.29, 105), (28.62, 111), (28.96, 125), (30.71, 121), (31.87, 101)]   # chords, top velocity
_NOTES = [(26.35, 94), (26.45, 93), (26.57, 89), (26.68, 100), (26.81, 95), (26.92, 97), (27.04, 102), (27.13, 79), (27.25, 94),
          (27.36, 85), (27.47, 102), (27.58, 86), (27.71, 103), (27.83, 99), (28.05, 102), (28.18, 90), (28.29, 105), (28.40, 76),
          (28.51, 76), (28.62, 111), (28.74, 94), (28.85, 104), (28.96, 125)] + [(t, 85) for t in _RUN] + [(30.71, 121)] + \
         [(t, v) for t, v in zip(_ARP, (81, 72, 75, 77, 74, 75, 95, 103))]
def _out(u): u = min(1.0, max(0.0, u)); return 1 - (1 - u) ** 3           # fast start, soft landing
def _pulse(t, t0, amp, decay=0.25): return amp * np.exp(-(t - t0) / decay) if t >= t0 else 0.0
def _step(t, t0, amp, dur): return amp * ease((t - t0) / dur) if t >= t0 else 0.0
def _creep(t, until=28.62): return 0 if t < 26.35 else 260 + 260 * ease((t - 26.35) / (until - 26.35))
# I, J, K (2026-11-13, the user: "at this exact frame the background will be fully brown"): the frame is the first of
# part II, 0:36.43 (frame 1093), on the soft G chord at 0:36.42 where the crossing ends. These are steered by how much of
# the frame is brown (a slightly bigger circle soon covers most of the frame, so steering the radius makes it fill
# early and then creep): the share follows an accelerating curve that reaches all of the frame exactly then.
COVERAGE_PLANS = ('I', 'J', 'K', 'J2', 'J3', 'J4', 'K2', 'K3', 'K4', 'K5', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'U', 'T1', 'T2', 'T3', 'T4', 'mine_k4', 'Y1')
FULL_AT = 33.146          # choreography time of video frame 1093 (0:36.433), part II's first frame
_GY, _GX = np.mgrid[0:H:12, 0:W:12].astype(np.float32)
def _coverage(r, bx):
    if r <= 0: return 0.0
    d = np.sqrt((_GX - bx) ** 2 + ((_GY - 720) * 1.15) ** 2); m = np.clip((r - d) / 420 + 0.5, 0, 1)
    return float((m * m * (3 - 2 * m)).mean())
def _radius_for(c, bx):
    lo, hi = 0.0, 4000.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if _coverage(mid, bx) < c: lo = mid
        else: hi = mid
    return hi
def _cov_plan(t, bx):
    P = AURA_PLAN; rB = lambda tt: _radius_B(tt)
    if P == 'I':    # B up to the chord at 0:35.04, then an accelerating glide into part II
        t0 = 31.87
        if t < t0: return None
        c0 = _coverage(rB(t0), bx); u = (t - t0) / (FULL_AT - t0); return c0 + (1 - c0) * u ** 2.5
    if P == 'J':    # B up to the leap chord; the arpeggio climbs to 60% in growing steps; from its chord an accelerating glide into part II
        if t < _ARP[0]: return None
        c0 = _coverage(rB(_ARP[0]), bx); w = [1.45 ** i for i in range(len(_ARP))]
        done = sum(wi * ease((t - tn) / 0.08) for wi, tn in zip(w, _ARP) if t >= tn) / sum(w)
        c = c0 + (0.60 - c0) * done
        if t >= 31.87: c = 0.60 + 0.40 * ((t - 31.87) / (FULL_AT - 31.87)) ** 2
        return c
    if P == 'K':    # one long acceleration from the loudest chord (0:31.85) into part II, with no steps
        t0 = 28.96
        if t < t0: return None
        c0 = _coverage(rB(t0), bx); u = (t - t0) / (FULL_AT - t0); return c0 + (1 - c0) * u ** 3
    # variants of J and K (2026-11-13, the user: "K and J are the most reasonable ... other ways: more speed, less speed,
    # more acceleration, maybe a regression, but at the end it accelerates fast"); all fully brown exactly at FULL_AT
    def arp_climb(t, top):
        c0 = _coverage(rB(_ARP[0]), bx); w = [1.45 ** i for i in range(len(_ARP))]
        done = sum(wi * ease((t - tn) / 0.08) for wi, tn in zip(w, _ARP) if t >= tn) / sum(w)
        return c0 + (top - c0) * done
    if P == 'J2':   # the arpeggio climbs higher (75%), then a sharper glide
        if t < _ARP[0]: return None
        return arp_climb(t, 0.75) if t < 31.87 else 0.75 + 0.25 * ((t - 31.87) / (FULL_AT - 31.87)) ** 3
    if P == 'J3':   # climb to 65%, recede to 50% through part II's soft opening, then a fast rush
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.65)
        if t < 32.55: return 0.65 - 0.15 * ease((t - 31.87) / (32.55 - 31.87))
        return 0.50 + 0.50 * ((t - 32.55) / (FULL_AT - 32.55)) ** 3
    if P == 'J4':   # after the arpeggio, one step on every note of part II's opening, each bigger, the last on the chord
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.60)
        w = [1.35 ** i for i in range(len(_OPEN))]; done = sum(wi * ease((t - tn) / 0.06) for wi, tn in zip(w, _OPEN) if t >= tn) / sum(w)
        return 0.60 + 0.40 * done
    if P in ('K2', 'K3', 'K5'):   # K's single speed-up from the loudest chord: K2 later and harder, K3 gentler, K5 exponential
        t0 = 28.96
        if t < t0: return None
        c0 = _coverage(rB(t0), bx); u = (t - t0) / (FULL_AT - t0)
        f = {'K2': u ** 5, 'K3': u ** 2, 'K5': (np.exp(6 * u) - 1) / (np.exp(6) - 1)}[P]
        return c0 + (1 - c0) * f
    if P == 'K4':   # K up to the chord at 0:35.04, a breath back in part II's soft opening, then a rush
        t0 = 28.96
        if t < t0: return None
        c0 = _coverage(rB(t0), bx)
        if t < 31.87: return c0 + (0.62 - c0) * ((t - t0) / (31.87 - t0)) ** 2
        if t < 32.55: return 0.62 - 0.14 * ease((t - 31.87) / (32.55 - 31.87))
        return 0.48 + 0.52 * ((t - 32.55) / (FULL_AT - 32.55)) ** 3
    if P in _R_PLANS: return _r_plan(P, t, bx, rB, arp_climb)
    if P == 'U' or P in _CURVE_FILES: return _user_cov(TM.new(t))
    return None
# R1-R8 (2026-11-13, the user: "more like K4 and J3 ... find more ways to make it interesting"): the colour pulls back,
# then rushes in; every one fully brown exactly at FULL_AT. Times are notes: 28.96 the loudest chord, 30.59 the run's
# top, 30.71 the leap chord, 31.87 the arpeggio's chord (0:35.04), _OPEN the soft opening of part II (0:35.55-0:36.42).
# U (2026-11-13): the user's own curve, drawn in the editor on the crossing page. AURA_CURVE is a JSON file (default
# aura_curve.json next to this script) with {"pts": [{"t", "c", "h1": [t, c], "h2": [t, c]}, ...]}: anchor points
# in VIDEO time and share of the frame that is brown, joined by cubic Bezier segments (a.h2 and b.h1 are the
# segment's control points), the same curve the page draws and previews.
# Named curves live in aura_curves/ (AURA=T1 reads aura_curves/T1.json; mine_k4 is the user's edit of K4, T1-T4 are
# made from it by aura_curves/make_t.py).
_CURVE = None
_CURVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aura_curves')
_CURVE_FILES = {f[:-5] for f in os.listdir(_CURVE_DIR) if f.endswith('.json')} if os.path.isdir(_CURVE_DIR) else set()
def _user_cov(T):
    global _CURVE
    if _CURVE is None:
        path = os.path.join(_CURVE_DIR, AURA_PLAN + '.json') if AURA_PLAN in _CURVE_FILES else \
               os.environ.get('AURA_CURVE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aura_curve.json'))
        _CURVE = json.load(open(path))['pts']
    pts = _CURVE
    if T < pts[0]['t']: return 0.0
    if T >= pts[-1]['t']: return 1.0
    for a, b in zip(pts, pts[1:]):
        if T <= b['t']:
            x0, y0 = a['t'], a['c']; x1, y1 = a['h2']; x2, y2 = b['h1']; x3, y3 = b['t'], b['c']
            lo, hi = 0.0, 1.0
            for _ in range(40):
                u = (lo + hi) / 2
                if (1 - u) ** 3 * x0 + 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3 * x3 < T: lo = u
                else: hi = u
            u = (lo + hi) / 2
            return min(1.0, max(0.0, (1 - u) ** 3 * y0 + 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3 * y3))
    return 1.0
_R_PLANS = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8')
def _seg(t, keys, c_start, t_start):
    # keys: (time, coverage, shape); the coverage moves from the previous key to this one with that shape
    t0, c0 = t_start, c_start
    for t1, c1, sh in keys:
        if t < t1:
            u = (t - t0) / (t1 - t0)
            f = {'ease': ease(u), 'in2': u ** 2, 'in3': u ** 3, 'in4': u ** 4, 'out': _out(u),
                 'exp': (np.exp(7 * u) - 1) / (np.exp(7) - 1), 'hold': 0.0}[sh]
            return c0 + (c1 - c0) * f
        t0, c0 = t1, c1
    return c0
def _r_plan(P, t, bx, rB, arp_climb):
    if P == 'R1':   # two breaths: the arpeggio climbs to 60%, back to 48%, a swell on the first notes of part II, back again, then the rush
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.60)
        return _seg(t, [(32.34, .48, 'ease'), (32.65, .62, 'ease'), (32.80, .52, 'ease'), (FULL_AT, 1, 'in3')], .60, 31.87)
    if P == 'R2':   # the deep tide: K's growth to 62%, then the colour sinks right back to 30%, then a long hard rush
        if t < 28.96: return None
        c0 = _coverage(rB(28.96), bx)
        return _seg(t, [(31.87, .62, 'in2'), (32.70, .30, 'ease'), (FULL_AT, 1, 'in4')], c0, 28.96)
    if P == 'R3':   # step back on each soft note: arpeggio to 65%, the first six notes of part II each pull it back a step
                    # (to 42%), the last four each push it forward, each step bigger, full on the chord
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.65)
        back = sum(ease((t - tn) / 0.07) for tn in _OPEN[:6] if t >= tn) / 6
        w = [1.8 ** i for i in range(4)]
        fwd = sum(wi * ease((t - tn) / 0.05) for wi, tn in zip(w, _OPEN[6:]) if t >= tn) / sum(w)
        return 0.65 - 0.23 * back + 0.58 * fwd
    if P == 'R4':   # hold your breath: K's growth to 65%, snaps back to 50% on the chord, almost still through the soft
                    # notes, then bursts in the last quarter of a second
        if t < 28.96: return None
        c0 = _coverage(rB(28.96), bx)
        return _seg(t, [(31.87, .65, 'in2'), (32.02, .50, 'out'), (32.91, .53, 'ease'), (FULL_AT, 1, 'in2')], c0, 28.96)
    if P == 'R5':   # a heartbeat while it recedes: arpeggio to 60%, sinking to 44%, a small beat on every note of part II's
                    # opening, the beats growing as it rushes in
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.60)
        base = _seg(t, [(32.65, .44, 'ease'), (FULL_AT, 1, 'in3')], .60, 31.87)
        beat = sum((0.10 + 0.025 * i) * np.exp(-(t - tn) / 0.10) for i, tn in enumerate(_OPEN) if t >= tn)
        return base + (1 - base) * min(0.6, beat) if t < FULL_AT else 1.0
    if P == 'R6':   # the slingshot: it keeps growing to 80% into part II, is pulled back to 58% on the notes at
                    # 0:36.1, then flies to full in the last 0.24 s
        if t < 28.96: return None
        c0 = _coverage(rB(28.96), bx)
        return _seg(t, [(32.65, .80, 'in2'), (32.91, .58, 'out'), (FULL_AT, 1, 'in2')], c0, 28.96)
    if P == 'R7':   # breathes twice with the music: a burst on the loudest chord, back during the run, out again on the leap
                    # chord and the arpeggio, back in part II's soft opening, then the rush
        if t < 28.96: return None
        c0 = _coverage(rB(28.96), bx)
        return _seg(t, [(29.36, .46, 'out'), (30.59, .34, 'ease'), (31.87, .64, 'in2'), (32.55, .46, 'ease'),
                        (FULL_AT, 1, 'in3')], c0, 28.96)
    if P == 'R8':   # back to him: arpeggio to 65%, then the colour shrinks right back around the black key (18%), and
                    # from him it explodes to the whole frame, exponentially, in the last half second
        if t < _ARP[0]: return None
        if t < 31.87: return arp_climb(t, 0.65)
        return _seg(t, [(32.65, .18, 'ease'), (FULL_AT, 1, 'exp')], .65, 31.87)
    return None
# the notes of part II's soft opening, 0:35.55-0:36.42 (choreography time), the last one the chord where the crossing ends
_OPEN = [32.34, 32.41, 32.47, 32.57, 32.65, 32.70, 32.80, 32.91, 33.02, 33.13]
def _radius_B(t):
    r = _creep(t)
    r += _pulse(t, 28.62, 80) + _pulse(t, 28.96, 160, 0.3) + (60 if t >= 28.62 else 0) + _step(t, 30.71, 120, 0.3)
    return r
def aura_radius(t, bx=300.0):
    P = AURA_PLAN
    if P in COVERAGE_PLANS:
        if t < 26.35: return 0
        c = _cov_plan(t, bx)
        if c is not None and c <= 0.0005: return 0
        return _radius_B(t) if c is None else (4000.0 if c >= 0.999 else _radius_for(min(c, 0.999), bx))
    if P == 'A':
        # grows with him while he creeps and chases, bursts on the stomp, then fills the frame
        # as the white one runs off, complete on the arrival chord at 33.11
        r = 0 if t < 26.35 else 260 + 260 * ease((t - 26.35) / 2.2)
        if t >= 28.55: r += 120 * np.exp(-(t - 28.55) / 0.25) + 60
        if t >= 30.91: r += 120 * ease((t - 30.91) / 0.6)
        if t >= 31.83: r += 2400 * ease((t - 31.83) / (33.11 - 31.83)) ** 1.6
        return r
    if t < 26.35: return 0
    r = _creep(t)
    if P == 'B':   # A's shape, every move on its note: the stomp chord, a bigger pulse on the loudest chord, the leap chord, the climb's chord
        r += _pulse(t, 28.62, 80) + _pulse(t, 28.96, 160, 0.3) + (60 if t >= 28.62 else 0) + _step(t, 30.71, 120, 0.3)
        if t >= 31.87: r += 2400 * ease((t - 31.87) / (33.13 - 31.87)) ** 1.6
    elif P == 'C':   # B up to the leap chord, then it speeds up with the rising arpeggio, each note a bigger step, and fills on its chord
        r += _pulse(t, 28.62, 80) + _pulse(t, 28.96, 160, 0.3) + (60 if t >= 28.62 else 0) + _step(t, 30.71, 120, 0.3)
        for i, tn in enumerate(_ARP): r += _step(t, tn, 5 * 1.45 ** i, 0.08)
        if t >= 31.87: r += 2200 * ease((t - 31.87) / 0.47)           # full by 32.34, the first note of part II
    elif P == 'D':   # a blast on the loudest chord (C, 28.96) to almost half the screen, a breath back, the leap chord, then full
        r += _step(t, 28.62, 60, 0.2)
        if t >= 28.96: r += 330 * _out((t - 28.96) / 0.4) - _step(t, 29.36, 60, 0.6)
        r += _step(t, 30.71, 160, 0.45)
        if t >= 31.87: r += 2200 * ease((t - 31.87) / 0.6)
    elif P == 'E':   # a heartbeat on every loud chord, as strong as the chord, each one leaving the colour a little further out
        for tn, v in _LOUD[:-1]:
            amp = 2.2 * (v - 60); r += _pulse(t, tn, amp, 0.22) + _step(t, tn, 0.45 * amp, 0.15)
        if t >= 31.87: r += 2400 * min(1.0, (t - 31.87) / 0.47) ** 3     # accelerating to full by 32.34
    elif P == 'F':   # in steps on every note, like his drawings: small steps on the run, growing steps on the arpeggio, a snap on the chord
        r += _pulse(t, 28.62, 80) + _pulse(t, 28.96, 160, 0.3) + (60 if t >= 28.62 else 0)
        r += sum(7 for tn in _RUN if t >= tn) + (60 if t >= 30.71 else 0) + sum(6 * 1.4 ** i for i, tn in enumerate(_ARP) if t >= tn)
        if t >= 31.87: r += 2600 * min(1.0, (t - 31.87) / 0.07)        # two frames
    elif P == 'G':   # driven by the notes themselves: every note pushes the edge out by its loudness, louder notes much more; full on the climb's chord
        e = sum((v / 127.0) ** 3 * ease((t - tn) / 0.12) for tn, v in _NOTES if t >= tn)
        r = 0 if t < 26.35 else 220 + 26 * e
        if t >= 31.87: r += 2300 * _out((t - 31.87) / 0.5)
    elif P == 'H':   # hardly moves until the arpeggio's top note, then snaps to full on the chord
        r = 0 if t < 26.35 else 240 + 120 * ease((t - 26.35) / 5.4)
        if t >= 31.87: r += 2600 * min(1.0, (t - 31.87) / 0.07)
    return r
def background(t, bx):
    r = aura_radius(t, bx)
    if r <= 0: return np.broadcast_to(BG1, (H, W, 3)).copy()
    d = np.sqrt((XX - bx) ** 2 + ((YY - 720) * 1.15) ** 2)
    m = np.clip((r - d) / 420 + 0.5, 0, 1); m = (m * m * (3 - 2 * m))[:, :, None]
    if t >= (FULL_AT if AURA_PLAN in COVERAGE_PLANS else 33.11): return np.broadcast_to(BG2, (H, W, 3)).copy()
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
    t = TM.old((f0 + i) / FPS)
    # the sheets are looked up by time, so each worker places the characters itself
    return frame(t, np.frombuffer(buf, np.uint8).reshape(H, W, 3)).tobytes()
if __name__ == '__main__':
    if sys.argv[1] == '--still':
        t = float(sys.argv[2]); from PIL import Image
        Image.fromarray(frame(t, grab(SRC, TM.new(t)))).save(sys.argv[3]); sys.exit()
    src, dst = sys.argv[1:3]
    t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (26.2333, 33.1333)
    f0, f1 = round(TM.new(t0) * FPS), round(TM.new(t1) * FPS)
    n = f1 - f0
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    if os.environ.get('LOSSLESS'): venc = ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24']
    else: venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', f'{f0 / FPS:.4f}', '-t', f'{n / FPS:.4f}', '-i', src, '-map', '0:v', '-map', '1:a?', *venc, '-c:a', 'aac', '-b:a', '192k', '-shortest', dst], stdin=subprocess.PIPE)
    def frames():
        for i in range(n):
            b = dec.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return
            yield i, b, f0
    with mp.Pool(4) as pool:
        for out in pool.imap(work, frames(), chunksize=4): enc.stdin.write(out)
    enc.stdin.close(); enc.wait(); dec.wait(); print('done', dst, n, 'frames')
