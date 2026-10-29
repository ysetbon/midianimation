# Builds the étude's two final videos from a notes render (render.js ... 11_sections):
# part I, the I -> II crossing, part II, the II -> III crossing, part III and the Coda, each with its
# character and look, then joined with the two soundtracks:
#   A: the new export (ethude1_19), B: the original recording, patched where the three notes were removed.
# Usage: python build_finals.py <notes.mp4> [outdir]        (needs ffmpeg, numpy and scipy)
# Finished segments are kept in outdir and skipped on a rerun; delete them (or pass --force) to remake them.
"""Usage: python build_finals.py <notes.mp4> [outdir] [--force]"""
import os, sys, subprocess, time

D = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
W, H, FPS, FRAMES, SECONDS = 1920, 1080, 30, 3664, 122.1334
ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709',
       '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart']


def frames(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries',
                          'stream=nb_read_frames', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout
    return int(out.strip() or 0)


def step(name, out, cmds, force):
    if os.path.exists(out) and not force:
        print(f'{name}: already made, skipping ({out})'); return
    t = time.time(); print(f'{name}: making ...', flush=True)
    for args, env in cmds:
        subprocess.run([PY, *args], env={**os.environ, **env}, check=True, cwd=os.path.dirname(args[0]))
    print(f'{name}: done in {time.time() - t:.0f}s', flush=True)


def main():
    args = [a for a in sys.argv[1:] if a != '--force']; force = '--force' in sys.argv
    if not args: sys.exit(__doc__ if __doc__ else 'usage: python build_finals.py <notes.mp4> [outdir]')
    src = os.path.abspath(args[0]); out = os.path.abspath(args[1] if len(args) > 1 else 'finals')
    os.makedirs(out, exist_ok=True)
    n = frames(src)
    print(f'notes render: {n} frames'); 
    if n < FRAMES: sys.exit(f'the notes render has {n} frames, {FRAMES} are needed: render it with DURATION=122.136 and AUDIO_SYNC=1.0434:0.04')
    o = lambda f: os.path.join(out, f)
    env = {'SRC': src}
    step('Part I', o('partI.mkv'), [([D + '/partI/anim.py', src, o('partI.mkv')],
         {**env, 'SPRITES': D + '/partI/poses', 'SHIFT': '384', 'SCALE': '1.90', 'PLAN': D + '/partI/plan_partI.json',
          'FLAT': '1', 'LOSSLESS': '1', 'BGCOLOR': '8c3b55'})], force)
    step('I -> II crossing', o('chase.mkv'), [
        ([D + '/chase/chase.py', src, o('crossing_long.mkv'), '26.2', '36.1333'], {**env, 'LOSSLESS': '1', 'BG2': '6e4a3c', 'S2': '1.693'}),
        ([D + '/chase/renote.py', src, o('crossing_long.mkv'), o('chase.mkv'), '26.1667'], env)], force)
    step('Part II', o('partII.mkv'), [([D + '/partII/partII.py', src, o('partII.mkv')], env)], force)
    step('II -> III crossing', o('t2.mkv'), [([D + '/t2/t2.py', src, o('t2.mkv'), '66.4667', '74.3667'], env)], force)
    step('Part III', o('partIII.mkv'), [([D + '/partIII/partIII.py', src, o('partIII.mkv')], env)], force)
    step('Coda', o('coda.mkv'), [([D + '/coda/coda.py', src, o('coda.mkv')], env)], force)
    segments = [('partI.mkv', 786), ('chase.mkv', 208), ('partII.mkv', 1000), ('t2.mkv', 237), ('partIII.mkv', 846), ('coda.mkv', 587)]
    for name, audio in (('etude1_final_A_new_export.mp4', 'A_new_export.flac'), ('etude1_final_B_patched.mp4', 'B_patched.flac')):
        t = time.time(); print(f'{name}: joining ...', flush=True)
        enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-i', os.path.join(D, 'audio', audio), '-map', '0:v', '-map', '1:a',
                                '-vf', 'scale=out_color_matrix=bt709:out_range=tv', *ENC, '-c:a', 'aac', '-b:a', '256k',
                                '-frames:v', str(FRAMES), '-t', str(SECONDS), o(name)], stdin=subprocess.PIPE)
        for seg, count in segments:
            dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', o(seg), '-frames:v', str(count), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                   stdout=subprocess.PIPE)
            while True:
                chunk = dec.stdout.read(W * H * 3 * 10)
                if not chunk: break
                enc.stdin.write(chunk)
            dec.wait()
        enc.stdin.close(); enc.wait()
        print(f'{name}: {frames(o(name))} frames, done in {time.time() - t:.0f}s', flush=True)
    print('finished:', o('etude1_final_A_new_export.mp4'), 'and', o('etude1_final_B_patched.mp4'))


if __name__ == '__main__':
    main()
