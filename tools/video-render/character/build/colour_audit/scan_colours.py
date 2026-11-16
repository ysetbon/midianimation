# scan_colours.py (2026-11-15): every frame of a final, what colour each thing in it is.
#
#   python3 scan_colours.py <final.mp4> <out.json> [--workers 4] [--every 1]
#
# For every frame (none skipped unless --every is given) it writes the section the frame belongs to (from
# build_finals.py's segment bounds), the background colour and how much of the frame it covers, and, for every colour
# in the characters' palettes, how many pixels of it are on screen and their median colour. Frames are read at half size
# with nearest-neighbour sampling, so no colour is a mix made by the scaling.
#
# The characters are found by their black outlines (the Black Key's body is black too): everything within ~36 px of
# a black stroke, with the holes filled, is "character". Palette colours are only counted there, so the notes (whose
# colours come close to the cheeks, the beret and the strip) never count. A pixel counts for a palette colour when it
# is the nearest palette colour, within MAXD, and so are its 8 neighbours (no anti-aliased edges; the thin beret line
# is counted without that).
# The background is the most common colour outside the characters; during the I -> II glow and the II -> III burst
# the background is a gradient, so its share of the frame drops (reported as `bg_share`).
import os, sys, json, subprocess, numpy as np
from multiprocessing import Pool
from scipy import ndimage

W, H, FPS = 960, 540, 30
# frame bounds of the six segments in a final built with the ethude_1_27 timemap (build_finals.py: bounds)
SECTIONS = [('Part I', 0), ('I -> II crossing', 865), ('Part II', 1093), ('II -> III (sleep, piano)', 2183),
            ('Part III', 2443), ('Coda', 3369)]
PALETTE = {  # name: (character, target colour)   targets from the reference frames (recolor.py, Z_12 at 1:13, coda piano)
    'cream card':      ('White Key', '#fbdebb'),
    'rim / whites':    ('White Key (also eye whites)', '#fcf8e7'),
    'lilac strip':     ('White Key', '#9e9bfa'),
    'orange cheeks':   ('White Key', '#fc9a47'),
    'green strip':     ('Black Key', '#70bd82'),
    'pink beret/skin': ('Black Key', '#fcb6a6'),
    'beret line':      ('Black Key', '#3a8c5a'),
    'green cheeks':    ('Black Key', '#649b6d'),
    'wood dark':       ('Brown Piano', '#6a3818'),
    'wood light':      ('Brown Piano', '#da8840'),
    'black':           ('outline / Black Key body', '#000000'),
}
MAXD = {'black': 40, 'beret line': 24}; MAXD_DEFAULT = 20
THIN = {'beret line'}   # 2-3 px at half size: counted without trimming the edges
NAMES = list(PALETTE); TGT = np.array([[int(PALETTE[k][1][i:i + 2], 16) for i in (1, 3, 5)] for k in NAMES], np.float32)

def hx(c): return '#%02x%02x%02x' % tuple(int(round(float(v))) for v in c)

def section(n):
    s = SECTIONS[0][0]
    for name, f0 in SECTIONS:
        if n >= f0: s = name
    return s

def analyse(fr):
    f = fr.astype(np.float32)
    black = fr.max(2) < 45
    lab, nl = ndimage.label(black)
    if nl:
        sizes = ndimage.sum(black, lab, range(1, nl + 1)); black = np.isin(lab, 1 + np.nonzero(sizes >= 30)[0])
    region = ndimage.binary_fill_holes(ndimage.uniform_filter(black.astype(np.float32), 37) > 1e-4)
    # background: the most common colour outside the characters
    out = fr[~region].reshape(-1, 3).astype(np.int32) if (~region).any() else fr.reshape(-1, 3).astype(np.int32)
    packed = (out[:, 0] << 16) | (out[:, 1] << 8) | out[:, 2]
    u, c = np.unique(packed, return_counts=True); m = u[np.argmax(c)]; mode = np.array([m >> 16, (m >> 8) & 255, m & 255], np.float32)
    share = float((np.abs(out - mode).max(1) <= 6).mean())
    res = {'bg': hx(mode), 'bg_share': round(share, 3), 'char_px': int(region.sum())}
    # palette colours inside the characters
    d = np.sqrt(((f[:, :, None, :] - TGT[None, None]) ** 2).sum(3))           # H x W x K
    k = d.argmin(2); dk = np.take_along_axis(d, k[..., None], 2)[..., 0]
    pal = {}
    for i, name in enumerate(NAMES):
        m_ = region & (k == i) & (dk <= MAXD.get(name, MAXD_DEFAULT))
        if name not in THIN: m_ = ndimage.binary_erosion(m_, structure=np.ones((3, 3), bool))
        n = int(m_.sum())
        if n >= 15: pal[name] = [n, hx(np.median(f[m_], 0))]
    res['pal'] = pal
    return res

def work(args):
    path, f0, f1, every = args
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{f0 / FPS:.6f}', '-i', path, '-frames:v', str(f1 - f0),
                          '-vf', f'scale={W}:{H}:flags=neighbor', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    rows = []; n = f0; sz = W * H * 3
    while n < f1:
        b = p.stdout.read(sz)
        if len(b) < sz: break
        if (n - f0) % every == 0:
            r = analyse(np.frombuffer(b, np.uint8).reshape(H, W, 3)); r['f'] = n; r['t'] = round(n / FPS, 3); r['section'] = section(n); rows.append(r)
        n += 1
    p.wait(); return rows

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    workers = int(opt.get('--workers', 4)); every = int(opt.get('--every', 1))
    total = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets',
                                '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip())
    step = 60; jobs = [(src, a, min(total, a + step), every) for a in range(0, total, step)]
    rows = []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap(work, jobs)):
            rows += r; print(f'{rows[-1]["f"] + 1 if rows else 0}/{total}', end='\r', flush=True)
    rows.sort(key=lambda r: r['f'])
    missing = sorted(set(range(0, total, every)) - {r['f'] for r in rows})
    json.dump({'video': os.path.basename(src), 'frames': total, 'fps': FPS, 'sections': SECTIONS,
               'palette': {k: v for k, v in PALETTE.items()}, 'missing': missing, 'rows': rows}, open(dst, 'w'), separators=(',', ':'))
    print(f'\n{len(rows)} frames scanned, {len(missing)} missing -> {dst}')
