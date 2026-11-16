# diff_finals.py <old.mp4> <new.mp4> [--threshold 14] [--gap 3]
#
# Which moments differ between two finals of the same length: both videos are streamed at 480x270 (never held in
# memory), and a frame counts as changed when any pixel differs by more than the threshold (0-255; 14 is above
# H.264 noise). Changed frames closer than --gap frames are reported as one range, in video time.
# Use it after every build: the answer should be exactly the moments you meant to change.
import sys, subprocess, numpy as np

def stream(path, w=480, h=270):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                            stdout=subprocess.PIPE)

def ts(f, fps=30): return f'{int(f / fps // 60)}:{f / fps % 60:05.2f}'

if __name__ == '__main__':
    a_path, b_path = sys.argv[1], sys.argv[2]; opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    thr, gap = int(opt.get('--threshold', 14)), int(opt.get('--gap', 3))
    A, B = stream(a_path), stream(b_path); n = 480 * 270 * 3; f = 0; changed = []
    while True:
        a, b = A.stdout.read(n), B.stdout.read(n)
        if len(a) < n or len(b) < n: break
        if np.abs(np.frombuffer(a, np.uint8).astype(np.int16) - np.frombuffer(b, np.uint8)).max() > thr: changed.append(f)
        f += 1
    runs = []
    for x in changed:
        if runs and x - runs[-1][1] <= gap: runs[-1][1] = x
        else: runs.append([x, x])
    print(f'{f} frames compared, {len(changed)} changed')
    for s, e in runs: print(f'  {ts(s)} - {ts(e)}   (frames {s}-{e})')
