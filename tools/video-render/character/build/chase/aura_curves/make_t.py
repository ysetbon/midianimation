# make_t.py: T1-T4 (2026-11-13), variations on the user's own edit of K4 (mine_k4.json, drawn in the crossing page's
# editor). What the user's curve does with the music: it grows into the loudest chord (fastest right on it, 0:31.85),
# climbs with the run and crests at 66% on its high notes (0:33.47); then it falls like a ball let go, slow at first and
# faster and faster through the loud leap chord, landing hardest at 21% exactly on the arpeggio's first soft note
# (0:34.04); it bounces in round arcs, 37% at the middle of the arpeggio and 39% on part II's first note (0:35.55),
# each landing on a note, rests lowest (20%) on the D3 at 0:35.94, and launches, faster and faster, onto the last chord
# (0:36.43). T1-T4 keep that bouncing-ball motion: gravity falls that land on notes, round hops, one late launch.
# Writes T1.json ... T4.json here, in the same Bezier format as the editor (AURA=T1 ... in chase.py). Video times.
import json, os
D = os.path.dirname(os.path.abspath(__file__))
START, END = 28.989, 36.433
MINE = json.load(open(os.path.join(D, 'mine_k4.json')))['pts']
def build(keys):
    # the user's own build, verbatim, up to the A4 at 0:33.14; then keys (t, c, shape[, apex]):
    # crest: soft rise to a soft top; fall: from rest, faster and faster, landing hard (a ball let go);
    # hop: a round arc up to `apex` and down onto the note; rest: still; launch: from rest, faster and faster upward
    pts = [dict(p, h1=list(p['h1']), h2=list(p['h2'])) for p in MINE[:4]]
    for k in keys:
        t, c, sh = k[:3]; a = pts[-1]; t0, c0 = a['t'], a['c']; dt = t - t0
        if sh == 'crest': h2, h1 = [t0 + dt / 3, c0 + (c - c0) * 0.6], [t - dt / 3, c]
        elif sh == 'fall': h2, h1 = [t0 + dt / 3, c0], [t0 + 2 * dt / 3, c0 - (c0 - c) / 3]
        elif sh == 'launch': h2, h1 = [t0 + dt / 3, c0], [t0 + 2 * dt / 3, c0 + (c - c0) / 3]
        elif sh == 'rest': h2, h1 = [t0 + dt / 3, c0], [t - dt / 3, c]
        elif sh == 'hop':
            lift = 4 / 3 * (k[3] - (c0 + c) / 2)
            h2, h1 = [t0 + dt / 3, min(1, c0 + lift)], [t - dt / 3, min(1, c + lift)]
        a['h2'] = h2; pts.append({'t': t, 'c': c, 'h1': h1, 'h2': None})
    pts[-1]['h2'] = [END + 0.1, 1.0]
    return [{'t': round(p['t'], 4), 'c': round(p['c'], 4), 'h1': [round(v, 4) for v in p['h1']], 'h2': [round(v, 4) for v in p['h2']]} for p in pts]
T = {
 # T1: yours, tidied onto the notes: crest on the high A (0:33.40), the fall lands on the E4 (0:34.04), one arc over the
 # arpeggio landing on the D4 (0:35.17), still through the silence, an arc onto part II's first note and down onto the
 # D3 (0:35.69), settling lowest on the next D3 (0:35.94), and the launch from the G at 0:36.05
 'T1': [(33.396, 0.66, 'crest'), (34.042, 0.21, 'fall'), (35.167, 0.24, 'hop', 0.37), (35.36, 0.24, 'rest'),
        (35.687, 0.25, 'hop', 0.39), (35.943, 0.20, 'fall'), (36.052, 0.20, 'rest'), (END, 1.0, 'launch')],
 # T2: a ball coming to rest: a higher crest (72%), a harder fall (to 15%), then each bounce lower and shorter, every
 # landing on a note (the chord 0:35.04, part II's first note 0:35.55, the D3s 0:35.69 and 0:35.94), then the launch
 'T2': [(33.396, 0.72, 'crest'), (34.042, 0.15, 'fall'), (35.036, 0.16, 'hop', 0.45), (35.547, 0.16, 'hop', 0.31),
        (35.687, 0.16, 'hop', 0.23), (35.943, 0.15, 'hop', 0.20), (36.052, 0.15, 'rest'), (END, 1.0, 'launch')],
 # T3: gathering strength: after the fall each bounce goes higher (30%, 42%, 55%), landing on the chord (0:35.04), on
 # part II's first note (0:35.55) and on the D3 (0:35.94), and from that landing it launches all the way
 'T3': [(33.396, 0.66, 'crest'), (34.042, 0.20, 'fall'), (35.036, 0.21, 'hop', 0.30), (35.547, 0.22, 'hop', 0.42),
        (35.943, 0.24, 'hop', 0.55), (END, 1.0, 'launch')],
 # T4: dribbled on the bass: your one big arc over the arpeggio, still through the silence, then a quick small bounce
 # on every bass note of part II's opening (A2, D3, G2, D3, G2: 0:35.55-0:36.05), each lower, and the launch
 'T4': [(33.396, 0.66, 'crest'), (34.042, 0.21, 'fall'), (35.167, 0.23, 'hop', 0.38), (35.547, 0.22, 'rest'),
        (35.687, 0.21, 'hop', 0.33), (35.802, 0.20, 'hop', 0.29), (35.943, 0.19, 'hop', 0.26), (36.052, 0.18, 'hop', 0.23),
        (END, 1.0, 'launch')],
}
if __name__ == '__main__':
    for k, keys in T.items():
        json.dump({'pts': build(keys)}, open(os.path.join(D, k + '.json'), 'w'), indent=1)
        print(k, len(keys) + 4, 'points')
