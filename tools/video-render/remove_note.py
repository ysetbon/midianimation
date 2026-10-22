# Remove one piano note from a recording, guided by the aligned MIDI:
# attenuate the note's partials that no other sounding note shares, in a
# narrow band around each, inside the time the note sounds, with smooth fades.
#
# Usage: python3 remove_note.py <in.f32> <out.f32>
#   in/out: raw 32-bit float stereo at 48 kHz, e.g.
#   ffmpeg -i recording.mp3 -f f32le -ac 2 -ar 48000 in.f32
#
# Set up here for the A3 at 98.516 s of ethude1_2026(17) (MIDI tick 18121,
# removed from midi/17_ethude1.mid). A3's even partials sit on the right
# hand's A4 and its 3rd and 9th on the E notes, so only the partials below
# are cut; the 5th is cut lopsidedly to keep the C# notes' 1108.7 Hz.
import numpy as np, sys, json
sr = 48000
x = np.fromfile(sys.argv[1], dtype=np.float32).reshape(-1, 2)
out = sys.argv[2]
# A3's partials that no other sounding note shares, measured on this recording
# (they fit a string stiffness of about 0.00026)
partials = [1, 5, 7, 11, 13, 15]
fn = [220.1, 1102.3, 1545.4, 2455.1, 2919.4, 3387.5]
# frame centres: every frame that covers the note's sound (from 98.516 s, with
# frames 0.34 s long) is fully cut; the cut ends before the A2 at 99.06 s
t_in0, t_in1 = 98.20, 98.34
# Hz below/above each partial: flat cut, then edge of the shoulder
BANDS = {1: (5, 5, 10, 10), 5: (6, 2.5, 11, 4.5), 7: (6, 6, 12, 12), 11: (7, 7, 14, 14),
         13: (7, 7, 14, 14), 15: (8, 8, 16, 16)}
t_out0, t_out1 = 98.90, 98.95
N, hop = 16384, 512
seg0, seg1 = int(97.6 * sr), int(99.8 * sr)
win = np.hanning(N).astype(np.float64)
freqs = np.fft.rfftfreq(N, 1 / sr)
y = x.copy()
for ch in range(2):
    s = x[seg0:seg1, ch].astype(np.float64)
    pad = np.concatenate([np.zeros(N), s, np.zeros(N)])
    acc = np.zeros_like(pad); norm = np.zeros_like(pad)
    for start in range(0, len(pad) - N, hop):
        frame = pad[start:start + N] * win
        Xf = np.fft.rfft(frame)
        tc = (seg0 - N + start + N / 2) / sr          # frame centre in seconds
        a = np.clip((tc - t_in0) / (t_in1 - t_in0), 0, 1) * np.clip((t_out1 - tc) / (t_out1 - t_out0), 0, 1)
        if a > 0:
            g = np.ones_like(freqs)
            for k, f in enumerate(fn):
                # flat-bottomed cut (piano unisons spread a partial over a few Hz)
                # with cosine shoulders; the 5th partial stays clear of the C#
                # notes' partial at 1108.7 Hz
                lo_flat, hi_flat, lo_edge, hi_edge = BANDS[partials[k]]
                d = freqs - f
                band = np.zeros_like(freqs)
                band[(d >= -lo_flat) & (d <= hi_flat)] = 1
                lo = (d < -lo_flat) & (d > -lo_edge); band[lo] = 0.5 + 0.5 * np.cos(np.pi * (-d[lo] - lo_flat) / (lo_edge - lo_flat))
                hi = (d > hi_flat) & (d < hi_edge); band[hi] = 0.5 + 0.5 * np.cos(np.pi * (d[hi] - hi_flat) / (hi_edge - hi_flat))
                g *= 1 - a * 0.985 * band                       # about -36 dB inside the flat part
            Xf *= g
        acc[start:start + N] += np.fft.irfft(Xf, n=N) * win
        norm[start:start + N] += win * win
    res = acc / np.maximum(norm, 1e-9)
    y[seg0:seg1, ch] = res[N:N + len(s)].astype(np.float32)
y.astype(np.float32).tofile(out)
json.dump({'partials_hz': [round(f, 1) for f in fn]}, open(out + '.json', 'w'))
print('partials removed at', [round(f, 1) for f in fn], 'Hz')
