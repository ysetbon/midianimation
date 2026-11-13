# still.py <part> <outdir> <video seconds...>: full frames (PNG-quality JPEG) from a part script at video times
import os, sys, importlib, subprocess, numpy as np
from PIL import Image
part, out = sys.argv[1:3]; times = [float(x) for x in sys.argv[3:]]
B = os.environ['B']; sys.path.insert(0, B); import timemap as TM
sys.path.insert(0, f'{B}/{part}'); SRC = os.environ['SRC']; W, H = 1920, 1080
def grab(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{(f - 0.5) / 30:.4f}', '-i', SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
if part == 'partI':
    os.environ.update(SPRITES=B + '/partI/poses', SHIFT='384', SCALE='1.90', PLAN=B + '/partI/plan_partI.json', FLAT='1', BGCOLOR='8c3b55')
    sys.argv = ['anim.py', 'x', 'y']; import anim as M
    render = lambda f: np.frombuffer(M.work((f, grab(f).tobytes())), np.uint8).reshape(H, W, 3)
else:
    if part == 'chase': os.environ.update(BG2='6e4a3c', S2='1.693'); os.environ.pop('NOSHRINK', None)
    if part == 'partII': os.environ['NOSHRINK'] = '1'
    M = importlib.import_module(part)
    render = lambda f: M.frame(TM.old(f / 30), grab(f))
os.makedirs(out, exist_ok=True)
for T in times:
    f = round(T * 30); Image.fromarray(render(f)).save(f'{out}/{part}_{f:04d}.jpg', quality=92)
print(part, len(times))
