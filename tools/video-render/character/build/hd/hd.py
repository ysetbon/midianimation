# The sharp redraws: get(part, key) gives the drawing at F x the old one's size (rgb, alpha, F), or None.
# Every size and anchor still comes from the old drawing; only the pixels come from here. NOHD=1 turns it off.
import os, numpy as np
_P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hd_sprites.npz')
_Z, _C = None, {}
def get(part, k):
    global _Z
    if os.environ.get('NOHD') or not os.path.exists(_P): return None
    if _Z is None: _Z = np.load(_P)
    key = f'{part}:{k}'
    if key + '_rgb' not in _Z.files: return None
    if key not in _C: _C[key] = (_Z[key + '_rgb'], _Z[key + '_a'], int(_Z['F']))
    return _C[key]
