# contact_sheet.py <video.mp4> <out_prefix> [--every 0.5] [--from 0] [--to end] [--cols 10] [--rows 9] [--width 240]
#
# A labelled overview of a video: one small frame every --every seconds, --cols x --rows per sheet, each frame with its
# video time in the corner. Writes <out_prefix>_1.jpg, _2.jpg, ... Good for finding moments (thumbnails, a pose to fix)
# and for checking a whole final at a glance.
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    every, t0 = float(opt.get('--every', 0.5)), float(opt.get('--from', 0))
    cols, rows, w = int(opt.get('--cols', 10)), int(opt.get('--rows', 9)), int(opt.get('--width', 240)); h = round(w * 9 / 16)
    args = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', src]
    if '--to' in opt: args += ['-t', str(float(opt['--to']) - t0)]
    args += ['-vf', f'fps={1 / every},scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(args, stdout=subprocess.PIPE); n = w * h * 3; i = 0; sheet = None; k = 0
    def flush():
        global sheet, k
        if sheet is not None: k += 1; sheet.save(f'{out}_{k}.jpg', quality=85); print(f'{out}_{k}.jpg')
        sheet = None
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        slot = i % (cols * rows)
        if slot == 0: flush(); sheet = Image.new('RGB', (cols * w, rows * h), (0, 0, 0))
        im = Image.fromarray(np.frombuffer(b, np.uint8).reshape(h, w, 3)); t = t0 + i * every
        ImageDraw.Draw(im).text((3, 2), f'{int(t // 60)}:{t % 60:04.1f}', fill=(255, 255, 0))
        sheet.paste(im, ((slot % cols) * w, (slot // cols) * h)); i += 1
    flush()
