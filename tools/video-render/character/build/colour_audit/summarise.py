# summarise.py (2026-11-15): scan_colours.py's per-frame JSON -> the colour page's data (data.js).
#
#   python3 summarise.py <scan.json> <out data.js>
#
# Per section: the background (each colour it took and for how many frames), which characters are on screen, and for
# each palette colour its typical value (median over the frames it is on screen in), how far it wanders, and how far that
# is from the reference colour. Then the events: background jumps (a frame whose plain background differs from the frame
# before by more than JUMP levels) and colour drifts (runs of frames where a colour is more than DRIFT levels from its
# section's typical value, with at least MINPX pixels of it on screen).
import sys, json, numpy as np

JUMP, DRIFT, MINPX = 2, 12, 150
PRESENT = {'White Key': ('cream card', 1500), 'Black Key': ('green strip', 150), 'Brown Piano': ('wood dark', 1500)}

def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
def hx(c): return '#%02x%02x%02x' % tuple(int(round(float(v))) for v in c)
def dist(a, b): return float(np.abs(rgb(a) - rgb(b)).max())   # the largest of the three channel differences, in levels
def ts(f, fps=30): return f'{int(f / fps // 60)}:{f / fps % 60:05.2f}'

def runs(frames):
    out = []
    for f in frames:
        if out and f - out[-1][1] <= 2: out[-1][1] = f
        else: out.append([f, f])
    return out

src, dst = sys.argv[1], sys.argv[2]
D = json.load(open(src)); rows = D['rows']; N = D['frames']; fps = D['fps']
names = list(D['palette'])
bounds = [s[1] for s in D['sections']] + [N]
sections = [[s[0], s[1], bounds[i + 1]] for i, s in enumerate(D['sections'])]
by_f = {r['f']: r for r in rows}

summary = []; drifts = []
for name, f0, f1 in sections:
    rs = [by_f[f] for f in range(f0, f1) if f in by_f]
    plain = [r for r in rs if r['bg_share'] >= 0.8]
    bgc = {}
    for r in rs: bgc[r['bg']] = bgc.get(r['bg'], 0) + 1
    bg_list = sorted(bgc.items(), key=lambda kv: -kv[1])
    chars = {c: sum(1 for r in rs if r['pal'].get(k, [0])[0] >= n) for c, (k, n) in PRESENT.items()}
    pal = {}
    for k in names:
        vals = [(r['f'], r['pal'][k][1]) for r in rs if k in r['pal'] and r['pal'][k][0] >= MINPX]
        if len(vals) < 3: continue
        arr = np.array([rgb(v) for _, v in vals]); med = np.median(arr, 0)
        lo, hi = np.percentile(arr, 5, 0), np.percentile(arr, 95, 0)
        dev = [(f, dist(v, hx(med))) for f, v in vals]
        far = [f for f, d in dev if d > DRIFT]
        for a, b in runs(far):
            worst = max((d, f) for f, d in dev if a <= f <= b)
            drifts.append({'section': name, 'colour': k, 'f0': a, 'f1': b, 'from': ts(a, fps), 'to': ts(b, fps),
                           'typical': hx(med), 'worst': by_f[worst[1]]['pal'][k][1], 'worst_at': ts(worst[1], fps), 'levels': round(worst[0])})
        pal[k] = {'frames': len(vals), 'typical': hx(med), 'lo': hx(lo), 'hi': hx(hi), 'spread': round(float((hi - lo).max())),
                  'target': D['palette'][k][1], 'off_target': round(dist(hx(med), D['palette'][k][1]))}
    summary.append({'name': name, 'f0': f0, 'f1': f1, 'from': ts(f0, fps), 'to': ts(f1 - 1, fps), 'frames': f1 - f0,
                    'scanned': len(rs), 'bg': bg_list[:6], 'bg_kinds': len(bg_list), 'plain_frames': len(plain),
                    'chars': chars, 'pal': pal})

jumps = []
for f in range(1, N):
    a, b = by_f.get(f - 1), by_f.get(f)
    if not a or not b or a['bg_share'] < 0.8 or b['bg_share'] < 0.8: continue
    d = dist(a['bg'], b['bg'])
    if d > JUMP:
        jumps.append({'f': f, 'at': ts(f, fps), 'before': a['bg'], 'after': b['bg'], 'levels': round(d),
                      'section_before': a['section'], 'section_after': b['section']})

series = {'bg': [by_f[f]['bg'] if f in by_f else '' for f in range(N)],
          'bgShare': [by_f[f]['bg_share'] if f in by_f else 0 for f in range(N)],
          'pal': {k: [by_f[f]['pal'][k][1] if f in by_f and k in by_f[f]['pal'] else '' for f in range(N)] for k in names},
          'cnt': {k: [by_f[f]['pal'][k][0] if f in by_f and k in by_f[f]['pal'] else 0 for f in range(N)] for k in names}}
out = {'video': D['video'], 'frames': N, 'fps': fps, 'scanned': len(rows), 'missing': D['missing'],
       'sections': sections, 'palette': [[k, *D['palette'][k]] for k in names], 'summary': summary,
       'jumps': jumps, 'drifts': drifts, 'series': series, 'rules': {'JUMP': JUMP, 'DRIFT': DRIFT, 'MINPX': MINPX}}
open(dst, 'w').write('window.AUDIT=' + json.dumps(out, separators=(',', ':')) + ';\n')
print(f'{len(rows)}/{N} frames; {len(jumps)} background jumps; {len(drifts)} colour drifts')
for j in jumps: print('  jump', j['at'], j['before'], '->', j['after'], j['levels'], j['section_before'], '->', j['section_after'])
for d in drifts: print('  drift', d['section'], d['colour'], d['from'], '-', d['to'], d['typical'], '->', d['worst'], d['levels'])
