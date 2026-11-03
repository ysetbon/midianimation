# The sharp redraws (2026-11-01): the user's ChatGPT redraws of the 97 softest drawings, one 2x2 sheet per four
# frames (redraw/grids). Each redraw is fitted onto its old drawing by shape (scale and position that make the
# two outlines overlap best) and resampled onto a canvas exactly F times the old one, so every size and anchor the
# part scripts measure from the old drawings stays the same; they only take their pixels from here (hd.py).
# usage: make_hd.py ../../redraw/redrawn_grids   (the redrawn sheets, as the user sent them: 25 in round 1, 35 in round 2)
# A fixed single frame in redraw/redrawn_singles/<folder>/<frame>.png (any size) replaces that frame's cell.
import sys, os, glob, csv, json, numpy as np
from PIL import Image
from scipy.signal import fftconvolve
from scipy.ndimage import map_coordinates, label
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import shadow_fix   # part I's ground shadows
import recolor   # part I's white key in the chase's colours
F = 2
B = os.path.dirname(os.path.abspath(__file__)) + '/..'
RD = B + '/../redraw'
SRC = {'1_partI_white_key': ('partI/poses/sprites.npz', lambda n: {'A': '16', 'B': '14', 'C': '15'}[n[6]] + '_' + str(int(n[7:9]))),
       '2_coda_brown_piano': ('coda/coda_sprites.npz', lambda n: 'Q_' + n.split('_Q')[1][:-4]),
       '3_crossing_brown_piano': ('t2/t2_sprites.npz', lambda n: 'P_' + n.split('_P')[1][:-4]),
       '4_coda_black_key': ('coda/coda_sprites.npz', lambda n: 'B_' + n.split('_B')[1][:-4]),
       '5_chase_black_key': ('chase/chase_sprites.npz', lambda n: 'K_' + n.split('_K')[1][:-4]),
       '6_partII_black_key': ('partII/partII_sprites.npz', lambda n: n.rsplit('_', 1)[1][0] + '_' + n.rsplit('_', 1)[1][1:-4]),
       '7_partIII_white_key': ('partIII/partIII_sprites.npz', lambda n: n.rsplit('_', 1)[1][0] + '_' + n.rsplit('_', 1)[1][1:-4]),
       '8_coda_white_key': ('coda/coda_sprites.npz', lambda n: 'J_' + n.rsplit('_', 1)[1][1:-4]),
       '9_chase_white_key': ('chase/chase_sprites.npz', lambda n: 'W_' + n.split('_W')[1][:-4])}
W, H = 1536, 1024; CW, CH = W // 2, H // 2; PAD = 26
CELL = {'top left': (0, 0), 'top right': (1, 0), 'bottom left': (0, 1), 'bottom right': (1, 1)}
def bbox(a, th):
    ys, xs = np.nonzero(a > th); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
cells = list(csv.DictReader(open(RD + '/grids/sheets.csv')))
grids = {os.path.basename(f): np.asarray(Image.open(f).convert('RGBA')).astype(np.float32) / 255 for f in glob.glob(sys.argv[1] + '/*.png')}
out = {}; report = []
for folder, (npz, keyof) in SRC.items():
    Z = np.load(B + '/' + npz)
    files = sorted(glob.glob(f'{RD}/{folder}/*.png'))
    olds = [np.asarray(Image.open(f).convert('RGBA')) for f in files]
    bbs = [bbox(o[..., 3], 10) for o in olds]
    s = min((CH - 2 * PAD) / max(b[3] - b[1] for b in bbs), (CW - 2 * PAD) / max(b[2] - b[0] for b in bbs))   # as on the sheets
    for f, o, b in zip(files, olds, bbs):
        rel = f[len(RD) + 1:]; row = next(r for r in cells if r['frame'] == rel); cx, cy = CELL[row['cell']]
        new = grids[os.path.basename(row['sheet'])][cy * CH:(cy + 1) * CH, cx * CW:(cx + 1) * CW]
        k = keyof(os.path.basename(f)); oa = Z[k + '_a'].astype(np.float32) / 255; h0, w0 = oa.shape
        single = f'{RD}/redrawn_singles/{rel}'
        if os.path.exists(single):   # a fixed single frame: scale it so it matches the old drawing's height, like a cell
            img = Image.open(single).convert('RGBA'); al_ = np.asarray(img)[..., 3]; ys_, xs_ = np.nonzero(al_ > 40)
            img = img.crop((xs_.min(), ys_.min(), xs_.max() + 1, ys_.max() + 1)); full = np.asarray(img).astype(np.float32) / 255
            g = (b[3] - b[1]) * s / img.height; img = img.resize((round(img.width * g), round(img.height * g)), Image.LANCZOS)
            px, py = 100 + (CW - img.width) // 2, 100 + CH - PAD - img.height
            cell = Image.new('RGBA', (CW + 200, CH + 200), (0, 0, 0, 0)); cell.alpha_composite(img, (px, py))
            new = np.asarray(cell).astype(np.float32) / 255   # the fit is found at sheet size, the pixels come from the full drawing
        else: full = None
        assert abs(o.shape[0] - h0) <= 1 and abs(o.shape[1] - w0) <= 1, (k, o.shape, oa.shape)
        # fit: old alpha at scale s*A against the new alpha; the best overlap (IoU) gives A and the shift
        na = (new[..., 3] > 0.5).astype(np.float32)[::2, ::2]
        fit_a = oa.copy()
        if npz.startswith('partI/'):   # the redraws have no ground shadow now: fit on the drawing alone
            orgb = Z[k + '_rgb'].astype(np.float32) / 255
            fit_a[(orgb.max(-1) < 0.15) & (oa < 0.8) & (np.arange(h0)[:, None] > 0.55 * h0)] = 0
        best = None
        for A in np.arange(0.86, 1.22, 0.01):
            sc = s * A / 2
            om = np.asarray(Image.fromarray((fit_a > 0.5).astype(np.uint8) * 255).resize((max(1, round(w0 * sc)), max(1, round(h0 * sc))), Image.BILINEAR)).astype(np.float32) / 255 > 0.5
            om = om.astype(np.float32)
            c = fftconvolve(na, om[::-1, ::-1], 'full'); i = np.unravel_index(c.argmax(), c.shape)
            iou = c[i] / (na.sum() + om.sum() - c[i])
            if best is None or iou > best[0]: best = (iou, A, i[0] - om.shape[0] + 1, i[1] - om.shape[1] + 1, sc)
        iou, A, oy, ox, sc = best
        # canvas F x the old one: old pixel (x, y) sits at new-cell pixel (2*ox + x*2*sc, 2*oy + y*2*sc)
        ys, xs = np.mgrid[0:h0 * F, 0:w0 * F].astype(np.float32)
        u = 2 * ox + (xs + 0.5) / F * 2 * sc - 0.5; v = 2 * oy + (ys + 0.5) / F * 2 * sc - 0.5
        if full is not None: u, v, src = (u + 0.5 - px) / g - 0.5, (v + 0.5 - py) / g - 0.5, full
        else: src = new
        # resample with the colours multiplied by their alpha, then divide it back out: the see-through edge pixels
        # keep their own colour (dividing straight colours by alpha turned the faint edge white, 2026-11-03)
        pm = np.concatenate([src[..., :3] * src[..., 3:4], src[..., 3:4]], -1)
        ch = [map_coordinates(pm[..., i], [v, u], order=1, mode='constant', cval=0) for i in range(4)]
        al = np.clip(ch[3], 0, 1); rgb = np.stack(ch[:3], -1) / np.maximum(al[..., None], 1e-3)   # un-premultiply the edges
        rgb = np.where(al[..., None] > 0.004, np.clip(rgb, 0, 1), 0)
        # elsewhere a ground shadow came back as opaque grey: make it see-through black of the same darkness, so the
        # scripts tint it with the background (a wide grey patch at the bottom of the drawing)
        sh = shadow_fix.oval(Z[k + '_rgb'], Z[k + '_a']) if npz.startswith('partI/') else None
        if npz.startswith('partI/') or folder in ('7_partIII_white_key', '8_coda_white_key', '9_chase_white_key'): rgb = recolor.apply(rgb, al)   # the white key: the colours of the chase's first frame
        if sh is not None:   # part I: the redraw's shadow out, a clean oval like the old one in
            rgb, al = shadow_fix.replace(rgb, al, sh, F)
        L = rgb.mean(-1); sat = rgb.max(-1) - rgb.min(-1)
        grey = (al > 0.05) & (sat < 0.08) & (L > 0.12) & (L < 0.85) & (sh is None)
        lab, n = label(grey)
        for j in range(1, n + 1):
            yy, xx = np.nonzero(lab == j)
            if len(yy) < 200 or yy.max() < 0.8 * al.shape[0] or (xx.max() - xx.min()) < 2.5 * (yy.max() - yy.min() + 1): continue
            m = lab == j; al[m] = al[m] * np.clip((1 - L[m]) * 1.1, 0, 1); rgb[m] = 0
        out[npz.split('/')[0] + ':' + k + '_rgb'] = (rgb * 255 + 0.5).astype(np.uint8)
        out[npz.split('/')[0] + ':' + k + '_a'] = (al * 255 + 0.5).astype(np.uint8)
        report.append((folder, k, round(float(iou), 3), round(float(A), 2)))
        print(folder, k, 'overlap', round(float(iou), 3), 'size', round(float(A), 2), flush=True)
np.savez_compressed(os.path.dirname(os.path.abspath(__file__)) + '/hd_sprites.npz', F=np.array(F), **out)
json.dump(report, open(os.path.dirname(os.path.abspath(__file__)) + '/hd_fit.json', 'w'), indent=0)
