# Builds the étude's two final videos from a notes render (render.js ... 11_sections):
# part I, the I -> II crossing, part II, the II -> III crossing, part III and the Coda, each with its
# character and look, then joined with the two soundtracks:
#   A: the new export (ethude1_19), B: the original recording, patched where the three notes were removed.
# Usage: python build_finals.py <notes.mp4> [outdir]        (needs ffmpeg, numpy and scipy)
# Finished segments are kept in outdir and skipped on a rerun; delete them (or pass --force) to remake them.
# For another recording of the MIDI (another tempo), --timemap plays the choreography on its timeline (see timemap.py)
# and --audio/--name make one final with that recording instead of A and B; --end sets where the video and sound end.
"""Usage: python build_finals.py <notes.mp4> [outdir] [--force] [--timemap scale:offset --audio <file> --name <out.mp4> --end <seconds>]"""
import os, sys, json, subprocess, time

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


def note_left(src, out):
    """leftmost note pixel per frame of the notes render (after part I's 384 px shift), as the scripts measure it"""
    w, h = 768, 540
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'crop=1536:1080:0:0,scale=768:540', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    import numpy as np
    left = []
    while True:
        b = dec.stdout.read(w * h * 3)
        if len(b) < w * h * 3: break
        cols = np.where((np.frombuffer(b, np.uint8).reshape(h, w, 3).max(2) > 24).any(0))[0]
        left.append(int(cols.min() * 2 + 384) if len(cols) else None)
    json.dump({'fps': FPS, 'noteLeft': left}, open(out, 'w'))


def main():
    argv = sys.argv[1:]; force = '--force' in argv; argv = [a for a in argv if a != '--force']
    opt = {}
    for k in ('--timemap', '--audio', '--name', '--end'):
        if k in argv: i = argv.index(k); opt[k] = argv[i + 1]; del argv[i:i + 2]
    if not argv: sys.exit(__doc__)
    src = os.path.abspath(argv[0]); out = os.path.abspath(argv[1] if len(argv) > 1 else 'finals')
    os.makedirs(out, exist_ok=True)
    o = lambda f: os.path.join(out, f)
    env = {'SRC': src}
    if '--timemap' in opt: os.environ['TIMEMAP'] = env['TIMEMAP'] = opt['--timemap']
    if '--end' in opt:   # after the last note (117.5 s of choreography) the rocking and the fade to black end exactly here
        os.environ['TIMEMAP_END'] = env['TIMEMAP_END'] = f"117.5:{FRAMES / FPS:.6f}:{float(opt['--end']):.6f}"
    sys.path.insert(0, D); import timemap as TM
    # where each part starts, in video frames (the choreography's frame numbers, played on the video's timeline)
    bounds = [0] + [round(TM.new(b / FPS) * FPS) for b in (786, 994, 1994, 2231, 3077)]
    if '--audio' in opt:
        finals = [(opt.get('--name', 'etude1_final.mp4'), os.path.abspath(opt['--audio']))]
        total = int(float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', finals[0][1]],
                                         capture_output=True, text=True).stdout) * FPS)
    else:
        finals = [('etude1_final_A_new_export.mp4', os.path.join(D, 'audio', 'A_new_export.flac')),
                  ('etude1_final_B_patched.mp4', os.path.join(D, 'audio', 'B_patched.flac'))]
        total = round(TM.new(FRAMES / FPS) * FPS)
    if '--end' in opt: total = round(float(opt['--end']) * FPS)
    n = frames(src)
    print(f'notes render: {n} frames, the video: {total}')
    if n < total: sys.exit(f'the notes render has {n} frames, {total} are needed: render it as long as the recording (DURATION, AUDIO_SYNC)')
    if 'TIMEMAP' in env:
        if force or not os.path.exists(o('notes_left.json')): note_left(src, o('notes_left.json'))
        env['NOTE_LEFT'] = o('notes_left.json')
    step('Part I', o('partI.mkv'), [([D + '/partI/anim.py', src, o('partI.mkv')],
         {**env, 'SPRITES': D + '/partI/poses', 'SHIFT': '384', 'SCALE': '1.90', 'PLAN': D + '/partI/plan_partI.json',
          'FLAT': '1', 'LOSSLESS': '1', 'BGCOLOR': '8c3b55'})], force)
    step('I -> II crossing', o('chase.mkv'), [
        ([D + '/chase/chase.py', src, o('crossing_long.mkv'), '26.2', '36.1333'], {**env, 'LOSSLESS': '1', 'BG2': '6e4a3c', 'S2': '1.693'}),
        ([D + '/chase/renote.py', src, o('crossing_long.mkv'), o('chase.mkv'), f'{(bounds[1] - 1) / FPS:.4f}'], env)], force)
    # part II: the black character always at full size; the vanish line keeps the notes off him (chosen 2026-10-30)
    step('Part II', o('partII.mkv'), [([D + '/partII/partII.py', src, o('partII.mkv')], {**env, 'NOSHRINK': '1'})], force)
    step('II -> III crossing', o('t2.mkv'), [([D + '/t2/t2.py', src, o('t2.mkv'), '66.4667', '74.3667'], env)], force)
    step('Part III', o('partIII.mkv'), [([D + '/partIII/partIII.py', src, o('partIII.mkv')], env)], force)
    step('Coda', o('coda.mkv'), [([D + '/coda/coda.py', src, o('coda.mkv'), f'{3077 / FPS:.6f}', f'{TM.old(total / FPS):.6f}'], env)], force)
    ends = bounds[1:] + [total]
    segments = list(zip(['partI.mkv', 'chase.mkv', 'partII.mkv', 't2.mkv', 'partIII.mkv', 'coda.mkv'], [b - a for a, b in zip(bounds, ends)]))
    for name, audio in finals:
        t = time.time(); print(f'{name}: joining ...', flush=True)
        enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-i', audio, '-map', '0:v', '-map', '1:a',
                                '-vf', 'scale=out_color_matrix=bt709:out_range=tv', *ENC, '-c:a', 'aac', '-b:a', '256k',
                                '-frames:v', str(total), '-t', f'{total / FPS:.4f}', o(name)], stdin=subprocess.PIPE)
        for seg, count in segments:
            dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', o(seg), '-frames:v', str(count), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                   stdout=subprocess.PIPE)
            got = 0
            while True:
                chunk = dec.stdout.read(W * H * 3 * 10)
                if not chunk: break
                enc.stdin.write(chunk); got += len(chunk)
            dec.wait()
            if got < count * W * H * 3: sys.exit(f'{seg} has {got // (W * H * 3)} frames, {count} are needed')
        enc.stdin.close(); enc.wait()
        print(f'{name}: {frames(o(name))} frames, done in {time.time() - t:.0f}s', flush=True)
    print('finished:', ' and '.join(o(name) for name, _ in finals))


if __name__ == '__main__':
    main()
