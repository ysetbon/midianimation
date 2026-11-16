# measure.py <part> <out.json>: for every video frame of a part, each character's outline (left, right, top, bottom px) and pose
import os, sys, json, importlib, numpy as np
part, out = sys.argv[1:3]
B = os.environ['B']; sys.path.insert(0, B); import timemap as TM
FPS = 30
bounds = [0] + [round(TM.new(b / FPS) * FPS) for b in (786, 994, 1994, 2231, 3077)] + [3927]
names = ['partI', 'chase', 'partII', 't2', 'partIII', 'coda']
i = names.index(part); f0, f1 = bounds[i], bounds[i + 1]
sys.path.insert(0, f'{B}/{part}')
def box(a, ox, oy):
    m = (a if a.ndim == 2 else a[:, :, 0]) > 0.05
    c = np.nonzero(m.any(0))[0]; r = np.nonzero(m.any(1))[0]
    return [int(ox + c.min()), int(ox + c.max()), int(oy + r.min()), int(oy + r.max())]
res = []
if part == 'partI':
    os.environ.update(SPRITES=B + '/partI/poses', SHIFT='384', SCALE='1.90', PLAN=os.environ.get('PLAN', B + '/partI/plan_partI.json'), FLAT='1', BGCOLOR='8c3b55')
    sys.argv = ['anim.py', 'x', 'y']; import anim as M
    for f in range(f0, f1):
        t = TM.old(f / FPS); e = M.pose_at(t)
        res.append(dict(f=f, t=t, white=dict(pose=f'{e[1]}_{e[2]}', start=e[0], box=None)))
    cache = {}
    for r in res:
        t = r['t']; e = M.pose_at(t); _, sh, po, x, fl = e
        if e[0] not in cache:
            ts = max(0.0, e[0]); t1 = next((s[0] for s in M.SHEET if s[0] > e[0] + 1e-6), e[0] + 0.4)
            sr = getattr(M, 'SHIFT_RIGHT', {}).get(e[0], 0)
            x = round(M.plan_centre(ts)) + sr; rlim = int(M.right_limit(ts, t1)) + ((M.PLAN['gap'] - M.GAP_R) if sr else 0)
            rgb, a, gx, gy = M.scaled(sh, po, fl); oy, ox = round(M.GROUND - gy), round(x - gx)
            cols = np.nonzero(a[:, :, 0].max(0) > 0.05)[0]; left, right = ox + cols.min(), ox + cols.max()
            if left < M.LEFTLIM: ox += M.LEFTLIM - left
            elif right > rlim: ox -= right - rlim
            cache[e[0]] = (box(a, ox, oy), rlim, x)
        r['white']['box'], r['white']['rlim'], r['white']['x'] = cache[e[0]]
elif part == 'chase':
    os.environ.update(BG2='6e4a3c', S2='1.693'); os.environ.pop('NOSHRINK', None)
    import chase as M
    for f in range(f0, f1):
        t = TM.old(f / FPS); s = M.cam_scale(t); d = dict(f=f, t=t)
        for nm, key, sheet in (('K', 'black', M.BLACK), ('W', 'white', M.WHITE)):
            p = M.place(nm, sheet, t, s)
            if p: e = M.at(sheet, t)[0]; d[key] = dict(pose=f'{nm}_{e[1]}', start=e[0], box=box(p[1], p[2], p[3]), rlim=M.PLACED[-1][5])
        res.append(d)
elif part in ('partII', 'partIII'):
    os.environ['NOSHRINK'] = '1'
    M = importlib.import_module(part)
    for f in range(f0, f1):
        t = TM.old(f / FPS); rgb, a, ox, oy, yoff, bw = M.place(t); e = M.at(t)[0]
        res.append(dict(f=f, t=t, **{'black' if part == 'partII' else 'white': dict(pose=e[1], start=e[0], box=box(a, ox, oy), rlim=M.PLACED[-1][4], y=e[3])}))
elif part == 't2':
    import t2 as M
    for f in range(f0, f1):
        t = TM.old(f / FPS); d = dict(f=f, t=t); e = M.at(M.BLACK, t)
        if e and e[1]:
            rgb, a, gx, gy = M.sprite(e[1], e[2]); ox, oy = round(M.CX - gx), round(M.GROUND - gy)
            if hasattr(M, 'black_ox'): ox = M.black_ox(e)
            else:
                cols = np.nonzero(a.max(0) > 0.05)[0]
                if ox + cols.max() > M.right_limit(e[0], e[0] + 0.4): ox -= ox + cols.max() - M.right_limit(e[0], e[0] + 0.4)
                if ox + cols.min() < M.LEFT: ox += M.LEFT - (ox + cols.min())
            d['black'] = dict(pose=e[1], start=e[0], box=box(a, ox, oy))
        p = M.at(M.PIANO, t)
        if p and p[1]:
            rgb, a, gx, gy = M.sprite(p[1]); lift = 0.0
            if t < M.FALL[1]:
                ts = M.FALL[0] + int((t - M.FALL[0]) / 0.2 + 1e-6) * 0.2; u = (ts - M.FALL[0]) / (M.FALL[1] - M.FALL[0]); lift = (M.GROUND - 220) * (1 - u ** 1.8)
            d['piano'] = dict(pose=p[1], start=p[0], box=box(a, round(M.PX - gx), round(M.GROUND - gy - lift)))
        d['cut'] = M.cut_at(t)
        res.append(d)
elif part == 'coda':
    import coda as M
    img = np.zeros((M.H, M.W, 3), np.float32)
    for f in range(f0, f1):
        t = TM.old(f / FPS); d = dict(f=f, t=t, cut=M.cut_at(t))
        sheets = [('piano', M.PIANO), ('white', M.WHITE), ('black', M.BLACK)] if t < M.HUG_IN[1] else [('hug', M.HUG)]
        for key, sheet in sheets:
            e = M.at(sheet, t)
            if not e or not e[1]: continue
            _, k, x, yoff, fl, ex = e; rgb, a, gx, gy = M.sprite(k, fl); ox, oy = round(x - gx), round(M.GROUND - gy - yoff)
            cols = np.nonzero(a.max(0) > 0.05)[0]
            if not ex and ox + cols.min() < M.LEFT: ox += M.LEFT - (ox + cols.min())
            d[key] = dict(pose=k, start=e[0], box=box(a, ox, oy))
        res.append(d)
if part == 'partIII':
    from crop import cut_at
    for r in res: r['cut'] = cut_at(r['t'])
json.dump(res, open(out, 'w')); print(part, f0, f1, len(res))
