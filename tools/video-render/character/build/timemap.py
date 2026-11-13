# The characters, camera and crossings are timed to the 115 BPM recording (choreography time, in seconds).
# TIMEMAP=scale:offset plays them on another recording of the same MIDI: video time T = scale * t + offset.
# TIMEMAP_END=knot:end:video_end plays the stretch after the last note (choreography time knot to end, the
# rocking and the fade to black) faster or slower so the video ends at video_end.
# NOTE_LEFT=<json> gives the leftmost note pixel per video frame, measured from the notes render in use;
# the scripts then read it in choreography time instead of their own measurements.
import os, json
SCALE, OFFSET = (float(x) for x in os.environ.get('TIMEMAP', '1:0').split(':'))
KNOT, END, VEND = (float(x) for x in os.environ.get('TIMEMAP_END', '1e9:1e9:1e9').split(':'))
FPS = 30
# TIMEMAP_SHIFT=T0:d,T1:d,... (2026-11-03, ethude_1_25): where the user shortened a passage, the music after it is d s
# earlier; the shift is eased linearly between the knots (on the TIMEMAP timeline, before the shift) and kept after
# the last one, so the characters stay on the notes without a jump
_SH = [tuple(float(x) for x in k.split(':')) for k in os.environ.get('TIMEMAP_SHIFT', '').split(',') if k]
def _shift(T0):
    if not _SH or T0 <= _SH[0][0]: return 0.0
    for (a, da), (b, db) in zip(_SH, _SH[1:]):
        if T0 <= b: return da + (db - da) * (T0 - a) / (b - a)
    return _SH[-1][1]
def _base(t): return t * SCALE + OFFSET
_vknot = _base(KNOT) - _shift(_base(KNOT))


def old(T):   # video time -> choreography time
    if T > _vknot: return KNOT + (T - _vknot) * (END - KNOT) / (VEND - _vknot)
    T0 = T
    for _ in range(40): T0 = T + _shift(T0)   # T0 - shift(T0) = T (the shift changes far slower than time)
    return (T0 - OFFSET) / SCALE


def new(t):   # choreography time -> video time
    if t > KNOT: return _vknot + (t - KNOT) * (VEND - _vknot) / (END - KNOT)
    T0 = _base(t); return T0 - _shift(T0)


def note_left(path):
    nl = json.load(open(path))['noteLeft']
    if not os.environ.get('NOTE_LEFT'): return nl
    m = json.load(open(os.environ['NOTE_LEFT']))['noteLeft']
    return [m[k] if 0 <= (k := round(new(f / FPS) * FPS)) < len(m) else None for f in range(len(nl))]
