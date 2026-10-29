# Recolour part II's notes in an already rendered segment (the I -> II chase), changing nothing else:
# the notes lie on top of everything, so each note pixel is re-blended over the background recovered under it.
# Usage: renote.py source.mp4 in.mkv out.mkv start_s [new_source.mp4]  (start_s: the source time of the segment's first frame)
# With new_source, the notes in in.mkv (as drawn from source) are replaced by new_source's notes, e.g. after a hand change.
import os, sys, subprocess, numpy as np
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D + '/../partII')
from recolor import notes_layer, TARGETS
W, H, FPS, BASE = 1920, 1080, 30, 10 / 255
SHIFT, CUT, FEATHER = 384, 480, 24
src, inp, dst, t0 = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
new = sys.argv[5] if len(sys.argv) > 5 else src
f0 = round(t0 * FPS)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', inp], capture_output=True, text=True).stdout)
dec_s = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', src, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
dec_n = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{(f0 - 0.5) / FPS:.4f}', '-i', new, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
dec_i = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', inp, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'medium', '-pix_fmt', 'rgb24', dst], stdin=subprocess.PIPE)
crop = np.clip((np.arange(W, dtype=np.float32) - CUT) / FEATHER, 0, 1)[None, :]
changed = 0
for i in range(n):
    s = np.frombuffer(dec_s.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
    img = np.frombuffer(dec_i.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    s2 = np.frombuffer(dec_n.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
    lift = lambda x: np.concatenate([np.zeros((H, SHIFT, 3), np.float32), np.clip((x.astype(np.float32) / 255 - BASE) / (1 - BASE), 0, 1)[:, :W - SHIFT]], axis=1)
    c0, a0 = notes_layer(lift(s), None); c1, a1 = notes_layer(lift(s2), TARGETS)
    n0 = np.clip((a0 - 0.02) / 0.98, 0, 1) * crop; n1 = np.clip((a1 - 0.02) / 0.98, 0, 1) * crop
    M = (np.abs(c1 - c0).max(2) > 1e-4) | (np.abs(n1 - n0) > 1e-4)
    if M.any():
        n0m = np.minimum(n0[M], 0.97)[:, None]
        bg = np.clip((img[M] - c0[M] * n0[M][:, None]) / (1 - n0m), 0, 1)
        img[M] = bg * (1 - n1[M][:, None]) + c1[M] * n1[M][:, None]; changed += 1
    enc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('done', dst, n, 'frames;', changed, 'with part II notes')
