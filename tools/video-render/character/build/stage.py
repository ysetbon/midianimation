# Where a character stands, worked out from the notes render (2026-11-11).
# Every part has a sheet of poses with a base position (where he stood before). plan() gives each sheet entry
# a shift to the right of that base: as far as the notes leave room (cap), and changing only on poses that
# travel. The part scripts say which poses those are:
#   ('hold',)            a planted pose: he stays exactly where the pose before left him
#   ('free', m)          a jump, a spin, a tumble: he may land up to m px away, either way
#   ('right', m[, keep]) a walk to the right: never back; ('left', m[, keep]) the same to the left.
#                        keep: of the walk's own step in the sheet, at least this much is left (so it still walks)
# The answer is the furthest-right plan that obeys all of that: every rule is "this entry is at most that entry
# plus a constant", so lowering values until nothing is broken (Bellman-Ford) ends at the highest plan there is.
# So he moves back in time for notes that come close, on the last travelling poses before them, and a new MIDI
# gives a new plan by itself. amount = 0 turns it off.


def opening(times, cap, stay, dt=0.05):
    """drop visits to the right shorter than `stay` seconds (he would go there only to come straight back)"""
    import numpy as np
    n = len(cap); t0, t1 = times[0], times[-1] + 0.4
    grid = np.arange(t0, t1, dt); idx = np.clip(np.searchsorted(np.array(times), grid + 1e-9, side='right') - 1, 0, n - 1)
    c = np.array(cap, float)[idx]; k = max(1, int(round(stay / dt)))
    ero = np.array([c[i:i + k].min() for i in range(len(c))])              # the lowest cap in the `stay` seconds from here
    opn = np.array([ero[max(0, i - k + 1):i + 1].max() for i in range(len(c))])   # the best such window that covers this moment
    return [float(min(cap[i], opn[idx == i].min())) if (idx == i).any() else float(cap[i]) for i in range(n)]


def plan(times, base, cap, moves, amount, fixed=None, stay=1.5, grid=20):
    """times, base (px), cap (px of room to the right of base) and moves per sheet entry -> shift per entry (px).
    fixed: {index: shift} for entries that must be exactly there (a hand-over); the planted poses after it stay with it."""
    n = len(times); fixed = fixed or {}
    if amount <= 0: return [0.0] * n
    # the room in steps of `grid` px (the top step is the amount itself), so he doesn't shuffle a few px on every pose
    room = [max(0.0, min(float(amount), float(c) // grid * grid)) for c in cap]
    keep = {}                                             # entries the short-visit filter must leave alone
    for i, v in fixed.items():
        keep[i] = min(float(v), max(0.0, float(cap[i]))) if v > 0 else 0.0
        j = i + 1
        while v > 0 and j < n and moves[j][0] == 'hold': keep[j] = max(0.0, min(float(amount), float(cap[j]))); j += 1
    up, down = [0.0] * n, [0.0] * n     # s[i] <= s[i-1] + up[i];  s[i-1] <= s[i] + down[i]
    for i in range(1, n):
        mv = moves[i]; d = base[i] - base[i - 1]          # the sheet's own step
        if mv[0] == 'hold': continue
        m = float(mv[1]); kp = float(mv[2]) if len(mv) > 2 else 0.0
        up[i] = max(0.0, m - d); down[i] = max(0.0, m + d)
        if mv[0] == 'right': down[i] = max(0.0, d - kp) if d > 0 else 0.0
        if mv[0] == 'left': up[i] = max(0.0, -d - kp) if d < 0 else 0.0
    def solve(s):
        s = list(s)
        for _ in range(n + 2):
            changed = False
            for rng in (range(1, n), range(n - 1, 0, -1)):
                for i in rng:
                    if s[i] > s[i - 1] + up[i] + 1e-9: s[i] = s[i - 1] + up[i]; changed = True
                    if s[i - 1] > s[i] + down[i] + 1e-9: s[i - 1] = s[i] + down[i]; changed = True
            if not changed: break
        return s
    def filt(s):
        o = opening(times, s, stay)
        for i, v in keep.items(): o[i] = v
        return o
    s = solve(filt(room))
    s = solve(filt(s))          # and no short trips left over once the steps are limited
    return [float(round(v)) for v in s]
