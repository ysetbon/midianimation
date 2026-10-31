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
_vknot = KNOT * SCALE + OFFSET


def old(T):   # video time -> choreography time
    if T > _vknot: return KNOT + (T - _vknot) * (END - KNOT) / (VEND - _vknot)
    return (T - OFFSET) / SCALE


def new(t):   # choreography time -> video time
    if t > KNOT: return _vknot + (t - KNOT) * (VEND - _vknot) / (END - KNOT)
    return t * SCALE + OFFSET


def note_left(path):
    nl = json.load(open(path))['noteLeft']
    if not os.environ.get('NOTE_LEFT'): return nl
    m = json.load(open(os.environ['NOTE_LEFT']))['noteLeft']
    return [m[k] if 0 <= (k := round(new(f / FPS) * FPS)) < len(m) else None for f in range(len(nl))]
