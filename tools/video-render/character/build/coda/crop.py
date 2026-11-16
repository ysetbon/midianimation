# Where the notes vanish around the start of the Coda: 25% of the width (480 px) through
# part III, widening to make room for the Black Key Piano's fall. CROP picks how.
import os
FROM, TO = 480, 1040
OPTIONS = {   # name: (start s, end s, how)
    'A': (101.00, 103.00, 'smooth'),   # early and gentle: while part III's long chord rings, done before he appears
    'B': (102.55, 103.30, 'smooth'),   # with the Coda: starts on its first notes, quick
    'C': (100.11, 103.30, 'smooth'),   # very early, slow: starts on part III's ta-da chord, a long glide
    'D': (102.55, 103.35, 'steps'),    # in 0.2 s jumps, like the characters' frames
    'E': (103.01, 103.01, 'snap'),     # all at once on the A5 note at 103.01
}
CHOICE = os.environ.get('CROP', 'B')   # chosen: with the Coda
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def cut_at(t):
    t0, t1, how = OPTIONS[CHOICE]
    if t < t0: return FROM
    if t >= t1: return TO
    if how == 'steps':
        n = round((t1 - t0) / 0.2); u = (int((t - t0) / 0.2) + 1) / n
    else: u = ease((t - t0) / (t1 - t0))
    return FROM + (TO - FROM) * u
